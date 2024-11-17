import abc
from dataclasses import dataclass
from datetime import datetime

from learn_anything.application.ports.committer import Commiter
from learn_anything.application.ports.playground import PlaygroundFactory
from learn_anything.entities.course.errors import CourseDoesNotExistError
from learn_anything.entities.submission.rules import create_code_submission
from learn_anything.entities.task.errors import TaskDoesNotExistError, ActorIsNotRegisteredOnCourseError, \
    CanNotSendSubmissionToNonPublishedCourse, AttemptsLimitExceededForTaskError
from learn_anything.entities.submission.models import PollTaskOptionID, PollSubmission, TextInputSubmission
from learn_anything.application.ports.auth.identity_provider import IdentityProvider
from learn_anything.application.ports.data.course_gateway import CourseGateway, RegistrationForCourseGateway
from learn_anything.application.ports.data.task_gateway import TaskGateway
from learn_anything.application.ports.data.submission_gateway import SubmissionGateway
from learn_anything.entities.task.models import TaskID, TaskType, TextInputTaskAnswer, PracticeTask, CodeTask, \
    CodeTaskTest
from learn_anything.entities.task.rules import option_is_correct, answer_is_correct
from learn_anything.entities.user.models import User, UserID


class CreateTaskSubmissionBaseInteractor(abc.ABC):
    def __init__(
            self,
            id_provider: IdentityProvider,
            submission_gateway: SubmissionGateway,
            task_gateway: TaskGateway,
            course_gateway: CourseGateway,
            playground_factory: PlaygroundFactory,
            commiter: Commiter,
            registration_for_course_gateway: RegistrationForCourseGateway
    ) -> None:
        self._id_provider = id_provider
        self._course_gateway = course_gateway
        self._task_gateway = task_gateway
        self._submission_gateway = submission_gateway
        self._registration_for_course_gateway = registration_for_course_gateway
        self._playground_factory = playground_factory
        self._commiter = commiter

    async def _ensure_actor_can_create_submission(self, actor: User, task: PracticeTask):
        course = await self._course_gateway.with_id(task.course_id)
        if not course:
            raise CourseDoesNotExistError(task.course_id)

        if actor.id == course.creator_id:
            return self._check_attempts_limit(actor_id=actor.id, task=task)

        actor_is_registered_on_course = await self._registration_for_course_gateway.exists(actor.id, course.id)
        if not actor_is_registered_on_course:
            raise ActorIsNotRegisteredOnCourseError(actor.id, task.course_id)

        if not course.is_published:
            raise CanNotSendSubmissionToNonPublishedCourse(course.id)

        return self._check_attempts_limit(actor_id=actor.id, task=task)

    async def _check_attempts_limit(self, actor_id: UserID, task: PracticeTask):
        self._submissions_number = await self._submission_gateway.get_user_submissions_number_for_task(
            user_id=actor_id,
            task_id=task.id,
        )
        if self._submissions_number + 1 > task.attempts_limit:
            raise AttemptsLimitExceededForTaskError(task_id=task.id)


@dataclass
class CreateCodeTaskSubmissionInputData:
    task_id: TaskID
    submission: str


@dataclass
class CreateCodeTaskSubmissionOutputData:
    failed_test_output: str | None = None
    failed_test_number: int | None = None


class CreateCodeTaskSubmissionInteractor(CreateTaskSubmissionBaseInteractor):
    async def execute(self, data: CreateCodeTaskSubmissionInputData) -> CreateCodeTaskSubmissionOutputData:
        actor = await self._id_provider.get_user()
        task = await self._task_gateway.get_code_task_with_id(data.task_id)
        if not task:
            raise TaskDoesNotExistError(data.task_id, type=TaskType.CODE)

        await self._ensure_actor_can_create_submission(actor=actor, task=task)

        tests_result_output, failed_test_idx = await self._check_submission(
            actor=actor,
            task=task,
            submission=data.submission,
        )

        submission = create_code_submission(
            user_id=actor.id,
            code=data.submission,
            task_id=task.id,
            tests_result_output=tests_result_output,
            attempt_number=self._submissions_number + 1
        )

        await self._submission_gateway.save_for_code_task(submission=submission)

        await self._commiter.commit()

        if not submission.is_correct:
            return CreateCodeTaskSubmissionOutputData(
                failed_test_output=tests_result_output,
                failed_test_number=failed_test_idx,
            )

    async def _check_submission(self, actor: User, task: CodeTask, submission: str):
        async with self._playground_factory.create(
                identifier=f'{actor.id}_{task.id}',
                code_duration_timeout=task.code_duration_timeout,
        ) as pl:
            self._pl = pl

            out, err = pl.execute_code(code=submission)
            for index, test in enumerate(task.tests):
                output, passed = await self._check_test(
                    test=test,
                    user_submission_output=out,
                    user_submission_stderr=err,
                )
                if not passed:
                    return output, index
            return 'ok', -1

    async def _check_test(
            self,
            test: CodeTaskTest,
            user_submission_output: str,
            user_submission_stderr: str,
    ) -> (str, bool):
        # you can use 'stdout' variable to retrieve an output from the user's code
        # and 'stderr' variable to retrieve a stderr from the user's code
        test_code = f'stdout = {user_submission_output}\nstderr = {user_submission_stderr}' + test.code

        out, err = self._pl.execute_code(code=test_code)
        if err:
            return f"Output:\n{out.decode()}\n{err.decode()}", False

        return out.decode(), True


@dataclass
class CreatePollTaskSubmissionInputData:
    task_id: TaskID
    selected_option: PollTaskOptionID


@dataclass
class CreatePollTaskSubmissionOutputData:
    is_correct: bool


class CreatePollTaskSubmissionInteractor(CreateTaskSubmissionBaseInteractor):
    async def execute(self, data: CreatePollTaskSubmissionInputData) -> CreatePollTaskSubmissionOutputData:
        actor = await self._id_provider.get_user()
        task = await self._task_gateway.get_poll_task_with_id(data.task_id)
        if not task:
            raise TaskDoesNotExistError(data.task_id, type=TaskType.POLL)

        await self._ensure_actor_can_create_submission(actor=actor, task=task)

        submission = PollSubmission(
            user_id=actor.id,
            selected_option=data.selected_option,
            task_id=task.id,
            created_at=datetime.now(),
            is_correct=option_is_correct(task, data.selected_option),
            attempt_number=self._submissions_number + 1
        )

        await self._submission_gateway.save_for_poll_task(submission=submission)

        await self._commiter.commit()

        return CreatePollTaskSubmissionOutputData(
            is_correct=submission.is_correct,
        )


@dataclass
class CreateTextInputTaskSubmissionInputData:
    task_id: TaskID
    value: str


@dataclass
class CreateTextInputTaskSubmissionOutputData:
    is_correct: bool


class CreateTextInputTaskSubmissionInteractor(CreateTaskSubmissionBaseInteractor):
    async def execute(self, data: CreateTextInputTaskSubmissionInputData) -> CreateTextInputTaskSubmissionOutputData:
        actor = await self._id_provider.get_user()
        task = await self._task_gateway.get_text_input_task_with_id(data.task_id)
        if not task:
            raise TaskDoesNotExistError(data.task_id, type=TaskType.TEXT_INPUT)

        await self._ensure_actor_can_create_submission(actor=actor, task=task)

        submission = TextInputSubmission(
            user_id=actor.id,
            task_id=task.id,
            created_at=datetime.now(),
            answer=data.value,
            is_correct=answer_is_correct(task, TextInputTaskAnswer(data.value)),
            attempt_number=self._submissions_number + 1
        )

        await self._submission_gateway.save_for_text_input_task(submission=submission)

        await self._commiter.commit()

        return CreateTextInputTaskSubmissionOutputData(
            is_correct=submission.is_correct,
        )
