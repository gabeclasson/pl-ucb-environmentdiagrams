# from pyquery import PyQuery as pq
import chevron

def generate(element_html, data):
    pass

def prepare(element_html, data):
    pass

def parse(element_html, data):
    # doc = pq(element_html)
    # inputs = doc(".pl-html-input")
    # for input in inputs:
    #     key = input.attr('pl-html-key')
    #     value = input.val()
    #     data["submitted_answers"][key] = value
    pass

def render(element_html, data):
    with open("pl-env-diagram.js") as script:
        with open('pl-env-diagram.css') as style:
            html_params = {
                'script': script.read(),
                'style': style.read()
            }
            with open("editor.mustache", "r") as f:
                return chevron.render(f, html_params).strip()

def grade(element_html, data):
    pass