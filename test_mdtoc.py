# Run:
# $ python3 -m pytest -v

import pytest
import mdtoc
import sys


def remove_indent(lines):
    return lines.replace("\n    ","\n")


def string_2_list(input):
    return input.split('\n')


@pytest.fixture
def mt():
    print("setup mdtoc")
    yield mdtoc.MdToc()
    print("teardown mdtoc")


def test_line_without_pound_is_not_header_(mt):
    assert mt.is_header("this is no header") is False


def test_line_without_space_after_pound_is_not_header(mt):
    assert mt.is_header("#this is no header") is False


def test_line_with_pound_is_header(mt):
    assert mt.is_header("# Introduction") is True


def test_line_with_two_pounds_is_header(mt):
    assert mt.is_header("## Introduction") is True


def test_line_with_ten_pounds_is_header(mt):
    assert mt.is_header("###### Introduction") is True


def test_line_with_eleven_pounds_is_not_header(mt):
    assert mt.is_header("####### Introduction") is False


def test_compose_name_attribute(mt):
    assert mt.compose_name_attribute("Introduction") == "introduction"


def test_anchor_name_with_spaces(mt):
    assert mt.compose_name_attribute("Introduction to python") == "introduction-to-python"

def test_anchor_name_with_swedish_characters(mt):
    assert mt.compose_name_attribute("Introduction to åäö") == "introduction-to-aao"

def test_anchor_name_with_ampersand(mt):
    assert mt.compose_name_attribute("Introduction to topic a & topic b") == "introduction-to-topic-a-and-topic-b"


def test_compose_anchor_tag(mt):
    assert mt.compose_anchor_tag("introduction-to-python") == \
        '<a name="introduction-to-python"></a>'


def test_parse_header_level(mt):
    assert mt.parse_header_level("# Introduction") == 1


def test_parse_headers(mt):
    i = []
    i.append("## header 1 with spaces")
    i.append("")
    i.append("bla bla bla")
    i.append("### header 2")
    i.append("")
    i.append("word word word")

    expected = []
    expected.append({'header': 'header 1 with spaces', 'level': 2, 'line': 1, 'tag': None})
    expected.append({'header': 'header 2', 'level': 3, 'line': 4, 'tag': None})

    o = mt.parse_headers(i)

    assert o == expected

def test_parse_headers_when_code_highlight_present(mt):
    i = []
    i.append("## header 1 with spaces")
    i.append("")
    i.append("bla bla bla")
    i.append("{% highlight cpp %}")
    i.append("## comment")
    i.append("int start() {")
    i.append("  std::cout << 'Name: ';")
    i.append("  std::getline(std::cin, name_);")
    i.append("}")
    i.append("{% endhighlight %}")
    i.append("### header 2")
    i.append("")
    i.append("word word word")

    expected = []
    expected.append({'header': 'header 1 with spaces', 'level': 2, 'line': 1, 'tag': None})
    expected.append({'header': 'header 2', 'level': 3, 'line': 11, 'tag': None})

    o = mt.parse_headers(i)

    assert o == expected

def test_parse_headers_with_existing_tag(mt):
    i = []
    i.append("## header 1 with spaces")
    i.append("")
    i.append("bla bla bla")
    i.append('### header 2<a name="header-2"></a>')
    i.append("")
    i.append("word word word")

    expected = []
    expected.append({'header': 'header 1 with spaces', 'level': 2, 'line': 1, 'tag': None})
    expected.append({'header': 'header 2', 'level': 3, 'line': 4, 'tag': 'header-2'})

    o = mt.parse_headers(i)

    assert o == expected

def test_parse_anchor_tag_name(mt):
    line = '### header 2<a name="header-2"></a>'
    expected = "header-2"
    o = mt.parse_anchor_tag_name(line)
    assert o == expected


def test_generate_tags_no_duplicates_existing_tag(mt):
    i = []
    i.append({'header': 'header 1 with spaces', 'level': 2, 'line': 1, 'tag': None})
    i.append({'header': 'Header 2', 'level': 3, 'line': 4, 'tag': 'header-2'})

    expected = []
    expected.append({'header': 'header 1 with spaces', 'level': 2, 'line': 1, 'tag': None, 'new_tag': 'header-1-with-spaces'})
    expected.append({'header': 'Header 2', 'level': 3, 'line': 4, 'tag': 'header-2', 'new_tag': None})

    assert expected == mt.generate_tags(i)

def test_generate_tags_with_duplicate(mt):
    i = []
    i.append({'header': 'header 1 with spaces', 'level': 2, 'line': 1, 'tag': None})
    i.append({'header': 'Header 2', 'level': 3, 'line': 4, 'tag': None})
    i.append({'header': 'Header 2', 'level': 4, 'line': 10, 'tag': None})

    expected = []
    expected.append("header-1-with-spaces")
    expected.append("header-2")
    expected.append("header-2-2")

    expected = []
    expected.append({'header': 'header 1 with spaces', 'level': 2, 'line': 1, 'tag': None, 'new_tag': 'header-1-with-spaces'})
    expected.append({'header': 'Header 2', 'level': 3, 'line': 4, 'tag': None, 'new_tag': 'header-2'})
    expected.append({'header': 'Header 2', 'level': 4, 'line': 10, 'tag': None, 'new_tag': 'header-2-2'})

    assert expected == mt.generate_tags(i)

def test_generate_tags_with_multiple_duplicates(mt):
    i = []
    i.append({'header': 'header 1 with spaces', 'level': 2, 'line': 1, 'tag': None})
    i.append({'header': 'Header 2', 'level': 3, 'line': 4, 'tag': None})
    i.append({'header': 'Header 2', 'level': 4, 'line': 10, 'tag': None})
    i.append({'header': 'Header 2', 'level': 4, 'line': 15, 'tag': None})

    expected = []
    expected.append("header-1-with-spaces")
    expected.append("header-2")
    expected.append("header-2-2")
    expected.append("header-2-3")

    expected = []
    expected.append({'header': 'header 1 with spaces', 'level': 2, 'line': 1, 'tag': None, 'new_tag': 'header-1-with-spaces'})
    expected.append({'header': 'Header 2', 'level': 3, 'line': 4, 'tag': None, 'new_tag': 'header-2'})
    expected.append({'header': 'Header 2', 'level': 4, 'line': 10, 'tag': None, 'new_tag': 'header-2-2'})
    expected.append({'header': 'Header 2', 'level': 4, 'line': 15, 'tag': None, 'new_tag': 'header-2-3'})

    assert expected == mt.generate_tags(i)


def test_generate_toc(mt):
    headers = []
    headers.append({'header': 'header 1 with spaces', 'level': 2, 'line': 1, 'tag': None, 'new_tag': 'header-1-with-spaces'})
    headers.append({'header': 'header 2', 'level': 3, 'line': 4, 'tag': 'header-2', 'new_tag': None})

    expected = []
    expected.append("* [header 1 with spaces](#header-1-with-spaces)")
    expected.append("    * [header 2](#header-2)")

    assert expected == mt.generate_toc(headers)

def test_generate_toc_skip_first_header(mt):
    headers = []
    headers.append({'header': 'header 1 with spaces', 'level': 2, 'line': 1, 'tag': None, 'new_tag': 'header-1-with-spaces'})
    headers.append({'header': 'header 2', 'level': 3, 'line': 4, 'tag': 'header-2', 'new_tag': None})
    headers.append({'header': 'header 3', 'level': 3, 'line': 8, 'tag': 'header-3', 'new_tag': None})

    expected = []
    expected.append("* [header 2](#header-2)")
    expected.append("* [header 3](#header-3)")

    assert expected == mt.generate_toc(headers, skip_headers=1)


def test_add_anchor_tags(mt):
    input_lines = []
    input_lines.append("## header 1 with spaces")
    input_lines.append("")
    input_lines.append("bla bla bla")
    input_lines.append("### header 2")
    input_lines.append("")
    input_lines.append("word word word")

    expect = []
    expect.append('## header 1 with spaces<a name="header-1-with-spaces"></a>')
    expect.append('')
    expect.append('bla bla bla')
    expect.append('### header 2<a name="header-2"></a>')
    expect.append('')
    expect.append('word word word')

    headers = mt.parse_headers(input_lines)
    headers_with_tags = mt.generate_tags(headers)

    output_lines = mt.add_anchor_tags(input_lines, headers_with_tags)

    print(output_lines)

    assert expect == output_lines

def test_add_anchor_tags_when_existing_tag(mt):
    input_lines = []
    input_lines.append('## header 1 with spaces')
    input_lines.append('')
    input_lines.append('bla bla bla')
    input_lines.append('### header 2<a name="header-2"></a>')
    input_lines.append('')
    input_lines.append('word word word')

    expect = []
    expect.append('## header 1 with spaces<a name="header-1-with-spaces"></a>')
    expect.append('')
    expect.append('bla bla bla')
    expect.append('### header 2<a name="header-2"></a>')
    expect.append('')
    expect.append('word word word')

    headers = mt.parse_headers(input_lines)
    headers_with_tags = mt.generate_tags(headers)

    output_lines = mt.add_anchor_tags(input_lines, headers_with_tags)

    print(output_lines)

    assert expect == output_lines


def test_add_toc(mt):
    input_lines = []
    input_lines.append("## Contents")
    input_lines.append("## header 1 with spaces")
    input_lines.append("")
    input_lines.append("bla bla bla")
    input_lines.append("### header 2")
    input_lines.append("")
    input_lines.append("word word word")

    expect = []
    expect.append('## Contents<a name="contents"></a>')
    expect.append('')
    expect.append("* [Contents](#contents)")
    expect.append("* [header 1 with spaces](#header-1-with-spaces)")
    expect.append("    * [header 2](#header-2)")
    expect.append('')
    expect.append('## header 1 with spaces<a name="header-1-with-spaces"></a>')
    expect.append('')
    expect.append('bla bla bla')
    expect.append('### header 2<a name="header-2"></a>')
    expect.append('')
    expect.append('word word word')

    output_lines = mt.add_toc(input_lines)

    print(output_lines)

    assert expect == output_lines

def test_add_toc_when_code_highlight_present(mt):
    input_lines = []
    input_lines.append("## Contents")
    input_lines.append("## header 1 with spaces")
    input_lines.append("")
    input_lines.append("bla bla bla")
    input_lines.append("{% highlight cpp %}")
    input_lines.append("## comment")
    input_lines.append("int start() {")
    input_lines.append("  std::cout << 'Name: ';")
    input_lines.append("  std::getline(std::cin, name_);")
    input_lines.append("}")
    input_lines.append("{% endhighlight %}")
    input_lines.append("### header 2")
    input_lines.append("")
    input_lines.append("word word word")

    expect = []
    expect.append('## Contents<a name="contents"></a>')
    expect.append('')
    expect.append("* [Contents](#contents)")
    expect.append("* [header 1 with spaces](#header-1-with-spaces)")
    expect.append("    * [header 2](#header-2)")
    expect.append('')
    expect.append('## header 1 with spaces<a name="header-1-with-spaces"></a>')
    expect.append('')
    expect.append('bla bla bla')
    expect.append("{% highlight cpp %}")
    expect.append("## comment")
    expect.append("int start() {")
    expect.append("  std::cout << 'Name: ';")
    expect.append("  std::getline(std::cin, name_);")
    expect.append("}")
    expect.append("{% endhighlight %}")
    expect.append('### header 2<a name="header-2"></a>')
    expect.append('')
    expect.append('word word word')

    output_lines = mt.add_toc(input_lines)

    print(output_lines)

    assert expect == output_lines

def test_parse_header_elements(mt):
    line = '### Header 1<a name="header-1"></a>'
    expect = []
    expect.append('###')
    expect.append('Header 1')
    expect.append('<a name="header-1"></a>')
    output = mt.parse_header_elements(line)
    assert expect == output

def test_header_elements_no_tag(mt):
    line = '### Header 1'
    expect = []
    expect.append('###')
    expect.append('Header 1')
    expect.append('')
    output = mt.parse_header_elements(line)
    assert expect == output

def test_insert_toc(mt):
    lines = []
    lines.append("## Contents")
    lines.append("## header 1 with spaces")
    lines.append("")
    lines.append("bla bla bla")
    lines.append("### header 2")
    lines.append("")
    lines.append("word word word")

    headers = mt.parse_headers(lines)
    headers_with_tags = mt.generate_tags(headers)
    toc = mt.generate_toc(headers_with_tags)
    lines_with_tags = mt.add_anchor_tags(lines, headers_with_tags)

    expect = []
    expect.append('## Contents<a name="contents"></a>')
    expect.append('')
    expect.append("* [Contents](#contents)")
    expect.append("* [header 1 with spaces](#header-1-with-spaces)")
    expect.append("    * [header 2](#header-2)")
    expect.append('')
    expect.append('## header 1 with spaces<a name="header-1-with-spaces"></a>')
    expect.append('')
    expect.append('bla bla bla')
    expect.append('### header 2<a name="header-2"></a>')
    expect.append('')
    expect.append('word word word')

    output = mt.insert_toc(lines_with_tags, toc)

    print(output)

    assert expect == output

def test_insert_toc_no_contents(mt, mocker):

    mocker.patch('builtins.print')
    mocker.patch('sys.exit')
    lines = []
    lines.append("## header 1 with spaces")
    lines.append("")
    lines.append("bla bla bla")
    lines.append("### header 2")
    lines.append("")
    lines.append("word word word")

    headers = mt.parse_headers(lines)
    headers_with_tags = mt.generate_tags(headers)
    toc = mt.generate_toc(headers_with_tags)
    lines_with_tags = mt.add_anchor_tags(lines, headers_with_tags)

    output = mt.insert_toc(lines_with_tags, toc)

    print.assert_called_with('ERROR: Document does not contain header with name Contents')
    sys.exit.assert_called()