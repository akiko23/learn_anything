import asyncio
import logging

import aio_pika
import msgpack
import pytest
import pytest_asyncio
from aio_pika.abc import AbstractChannel
from aio_pika.abc import ExchangeType
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

import learn_anything.course_platform.adapters.persistence.tables  # noqa
from learn_anything.course_platform.adapters.persistence.tables.user import users_table
from learn_anything.course_platform.domain.entities.user.enums import UserRole

START_BOT_EVENT = {
    'update_id': 128920819, 'message': {'message_id': 7721, 'date': 1734435446,
                                        'chat': {'id': 818525681, 'type': 'private', 'title': None,
                                                 'username': 'Mutual_exclusion', 'first_name': 'Fimoz',
                                                 'last_name': 'Fimozovich', 'is_forum': None, 'accent_color_id': None,
                                                 'active_usernames': None, 'available_reactions': None,
                                                 'background_custom_emoji_id': None, 'bio': None, 'birthdate': None,
                                                 'business_intro': None, 'business_location': None,
                                                 'business_opening_hours': None, 'can_set_sticker_set': None,
                                                 'custom_emoji_sticker_set_name': None, 'description': None,
                                                 'emoji_status_custom_emoji_id': None,
                                                 'emoji_status_expiration_date': None,
                                                 'has_aggressive_anti_spam_enabled': None, 'has_hidden_members': None,
                                                 'has_private_forwards': None, 'has_protected_content': None,
                                                 'has_restricted_voice_and_video_messages': None,
                                                 'has_visible_history': None, 'invite_link': None,
                                                 'join_by_request': None, 'join_to_send_messages': None,
                                                 'linked_chat_id': None, 'location': None,
                                                 'message_auto_delete_time': None, 'permissions': None,
                                                 'personal_chat': None, 'photo': None, 'pinned_message': None,
                                                 'profile_accent_color_id': None,
                                                 'profile_background_custom_emoji_id': None, 'slow_mode_delay': None,
                                                 'sticker_set_name': None, 'unrestrict_boost_count': None},
                                        'message_thread_id': None,
                                        'from_user': {'id': 818525681, 'is_bot': False, 'first_name': 'Fimoz',
                                                 'last_name': 'Fimozovich', 'username': 'Mutual_exclusion',
                                                      'language_code': 'en', 'is_premium': True,
                                                      'added_to_attachment_menu': None, 'can_join_groups': None,
                                                      'can_read_all_group_messages': None,
                                                      'supports_inline_queries': None, 'can_connect_to_business': None,
                                                      'has_main_web_app': None}, 'sender_chat': None,
                                        'sender_boost_count': None, 'sender_business_bot': None,
                                        'business_connection_id': None, 'forward_origin': None,
                                        'is_topic_message': None, 'is_automatic_forward': None,
                                        'reply_to_message': None, 'external_reply': None, 'quote': None,
                                        'reply_to_story': None, 'via_bot': None, 'edit_date': None,
                                        'has_protected_content': None, 'is_from_offline': None, 'media_group_id': None,
                                        'author_signature': None, 'text': '/start', 'entities': [
            {'type': 'bot_command', 'offset': 0, 'length': 6, 'url': None, 'user': None, 'language': None,
             'custom_emoji_id': None}], 'link_preview_options': None, 'effect_id': None, 'animation': None,
                                        'audio': None, 'document': None, 'paid_media': None, 'photo': None,
                                        'sticker': None, 'story': None, 'video': None, 'video_note': None,
                                        'voice': None, 'caption': None, 'caption_entities': None,
                                        'show_caption_above_media': None, 'has_media_spoiler': None, 'contact': None,
                                        'dice': None, 'game': None, 'poll': None, 'venue': None, 'location': None,
                                        'new_chat_members': None, 'left_chat_member': None, 'new_chat_title': None,
                                        'new_chat_photo': None, 'delete_chat_photo': None, 'group_chat_created': None,
                                        'supergroup_chat_created': None, 'channel_chat_created': None,
                                        'message_auto_delete_timer_changed': None, 'migrate_to_chat_id': None,
                                        'migrate_from_chat_id': None, 'pinned_message': None, 'invoice': None,
                                        'successful_payment': None, 'refunded_payment': None, 'users_shared': None,
                                        'chat_shared': None, 'connected_website': None, 'write_access_allowed': None,
                                        'passport_data': None, 'proximity_alert_triggered': None, 'boost_added': None,
                                        'chat_background_set': None, 'forum_topic_created': None,
                                        'forum_topic_edited': None, 'forum_topic_closed': None,
                                        'forum_topic_reopened': None, 'general_forum_topic_hidden': None,
                                        'general_forum_topic_unhidden': None, 'giveaway_created': None,
                                        'giveaway': None, 'giveaway_winners': None, 'giveaway_completed': None,
                                        'video_chat_scheduled': None, 'video_chat_started': None,
                                        'video_chat_ended': None, 'video_chat_participants_invited': None,
                                        'web_app_data': None, 'reply_markup': None, 'forward_date': None,
                                        'forward_from': None, 'forward_from_chat': None,
                                        'forward_from_message_id': None, 'forward_sender_name': None,
                                        'forward_signature': None, 'user_shared': None}, 'edited_message': None,
    'channel_post': None, 'edited_channel_post': None, 'business_connection': None, 'business_message': None,
    'edited_business_message': None, 'deleted_business_messages': None, 'message_reaction': None,
    'message_reaction_count': None, 'inline_query': None, 'chosen_inline_result': None, 'callback_query': None,
    'shipping_query': None, 'pre_checkout_query': None, 'purchased_paid_media': None, 'poll': None, 'poll_answer': None,
    'my_chat_member': None, 'chat_member': None, 'chat_join_request': None, 'chat_boost': None,
    'removed_chat_boost': None
}


USER = {'id': 818525681, 'fullname': 'Fimoz Fimozovich', 'username': 'kekeke23', 'role': UserRole.BOT_OWNER}


@pytest_asyncio.fixture(scope='module', loop_scope="session")
async def _prepare_db(db_session: AsyncSession):
    insert_user_stmt = insert(users_table).values(
        USER
    )
    await db_session.execute(insert_user_stmt)
    await db_session.commit()


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.usefixtures('_prepare_db', '_init_consumer')
async def test_get_all_courses(rmq_channel: AbstractChannel):
    logging.info('Rmq channel: %s', rmq_channel)

    queue_name = 'tg_updates'

    exchange = await rmq_channel.declare_exchange(queue_name, ExchangeType.TOPIC, durable=True)
    queue = await rmq_channel.declare_queue(name=queue_name, durable=True)
    await queue.bind(
        exchange,
        queue_name,
    )
    await exchange.publish(
        message=aio_pika.Message(
            body=msgpack.packb(START_BOT_EVENT),
        ),
        routing_key=queue_name,
    )

    # giving consumer a time to process and ack message
    await asyncio.sleep(3)

    after_pub_queue = await rmq_channel.get_queue(name=queue_name)
    assert after_pub_queue.declaration_result.message_count == 0
