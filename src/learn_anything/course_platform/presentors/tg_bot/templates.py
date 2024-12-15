from jinja2 import Template

python_code_tm = Template(
    (
        '<pre><code class="language-python">'
        '{{ code | e }}'
        '</code></pre>'
    )
)

pre_tm = Template(
    (
        '<pre>'
        '{{ content | e }}'
        '</pre>'
    )
)
