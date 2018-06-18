import argparse
import re
import sys

# Header structure
# ================
#
# ### Header title<a name="header-title"></a>
# |   |           |        |
# Pounds          |        |
#     Header title|        |
#                 Anchor tag
#                          Name attribute

class MdToc:

    def __init__(self):
        self.regexp_header = re.compile(r"^#{1,10} ")
        self.regexp_anchor_tag = re.compile(r"<a name=.{1,50}></a>$")
        self.HEADER_LEVEL_SPACES_INDENT = 4
        self.ANCHOR_TAG_PREFIX = '<a name="'
        self.ANCHOR_TAG_POSTFIX = '"></a>'
        self.TOC_HEADER = "Contents"

    def is_header(self, line):
        result = self.regexp_header.match(line)
        if result is None:
            return False
        else:
            return True

    def compose_name_attribute(self, header_text):
        header_lowercase = header_text.lower()
        header_no_spaces = header_lowercase.replace(' ', '-')
        return header_no_spaces

    def compose_anchor_tag(self, anchor_name):
        return self.ANCHOR_TAG_PREFIX + anchor_name + self.ANCHOR_TAG_POSTFIX

    def parse_header_elements(self, line):
        header_elements = []

        match_pounds = self.regexp_header.search(line)
        match_tag = self.regexp_anchor_tag.search(line)

        pounds = match_pounds.group()
        pounds = pounds.rstrip(' ') 

        title_start_pos = match_pounds.end()
        title_end_pos = match_tag.start() if match_tag else len(line) 
        header_title = line[title_start_pos:title_end_pos]

        anchor_tag = match_tag.group() if match_tag else ''

        header_elements.append(pounds)
        header_elements.append(header_title)
        header_elements.append(anchor_tag)

        return header_elements
        

    def parse_header_level(self, line):
        header_elements = self.parse_header_elements(line)
        pounds = header_elements[0]
        level = pounds.count('#')
        return level

    def parse_header_title(self, line):
        header_elements = self.parse_header_elements(line)
        header_title = header_elements[1]
        return header_title

    def parse_anchor_tag_name(self, line):
        header_elements = self.parse_header_elements(line)
        anchor_tag = header_elements[2]
        if anchor_tag == '':
            return None
        anchor_tag_split = anchor_tag.split('"')
        anchor_tag_name = anchor_tag_split[1]
        return anchor_tag_name

    def parse_header(self, line, line_number):
        header = {'header': self.parse_header_title(line),
                  'level' : self.parse_header_level(line),
                  'line'  : line_number,
                  'tag'   : self.parse_anchor_tag_name(line)}
        return header

    def parse_headers(self, lines):
        toc = []

        for index, line in enumerate(lines):
            line_number = index + 1
            if self.is_header(line):
                header = self.parse_header(line, line_number)
                toc.append(header)

        return toc


    def generate_non_duplicate_name_attribute(self, base_tag, tags):
        tag = base_tag
        counter = 2
        while tag in tags:
            tag = base_tag + '-' + str(counter)
            counter += 1
        return tag


    def generate_tags(self, headers):
        tags = []

        for header in headers:
            header['new_tag'] = None
            if header['tag'] is None:
                tag = self.compose_name_attribute(header['header'])
                tag = self.generate_non_duplicate_name_attribute(tag, tags)
                header['new_tag'] = tag
            else:
                tag = header['tag']
            tags.append(tag)

        return headers

    def header_level_min(self, headers):
        header_level_min = headers[0]['level']
        for header in headers:
            if header['level'] < header_level_min:
                header_level_min = header['level']
        return header_level_min


    def generate_toc(self, headers, skip_headers=0):
        toc = []
        headers_in_toc = headers[skip_headers:len(headers)]
        header_level_min = self.header_level_min(headers_in_toc)

        for header in headers_in_toc:
            toc_line = ""
            spaces = self.HEADER_LEVEL_SPACES_INDENT * (header['level'] - header_level_min)
            while len(toc_line) < spaces:
                toc_line += ' '
            toc_line += '*'
            toc_line += ' ['
            toc_line += header['header'].rstrip()
            toc_line += '](#'
            if header['tag'] is None:
                toc_line += header['new_tag'].rstrip()
            else:
                toc_line += header['tag'].rstrip()
            toc_line += ')'
            toc.append(toc_line)

        return toc


    def add_anchor_tags(self, lines, headers):
        output_lines = lines

        for header in headers:
            output_line = output_lines[header['line']-1].rstrip()
            if header['tag'] is None:
                output_line += self.compose_anchor_tag(header['new_tag'])
            output_lines[header['line']-1] = output_line

        return output_lines


    def add_toc(self, lines, skip_headers=0):
        output_lines = []

        headers = self.parse_headers(lines)
        headers_with_tags = self.generate_tags(headers)
        toc = self.generate_toc(headers_with_tags, skip_headers)
        content_with_tags = self.add_anchor_tags(lines, headers_with_tags)
        output_lines = self.insert_toc(content_with_tags, toc)

        return output_lines

    def insert_toc(self, lines_with_tags, toc):
        output = []
        insert_toc = False
        insert_toc_done = False

        for line in lines_with_tags:
            if self.is_header(line):
                if self.TOC_HEADER == self.parse_header_title(line):
                    insert_toc = True
                    output.append(line)
                    output.append('')
                    output += toc
                    output.append('')
                    insert_toc_done = True
                else:
                    insert_toc = False

            if not insert_toc:
                output.append(line)

        if not insert_toc_done:
            print('ERROR: Document does not contain header with name Contents')
            sys.exit(1)

        return output

def parse_command_line_arguments():

    parser_help_text="""Add table of contents to markdown file

mdtoc will create a table of contents and insert below
the header named Contents. Any existing lines in the
Contents section will be removed. An error message
will be emitted if no Contents header is found in
the input file.

Example:

    $ python3 mdtoc.py article.md

article.md before:

    # Contents
    # Header 1
    Some text between header 1 and 2
    
    ## Header 2
    Some text below header 2

article.md after:

    # Contents<a name="contents"></a>
    
    * [Contents](#contents)
    * [Header 1](#header-1)
        * [Header 2](#header-2)

    # Header 1<a name="header-1"></a>
    Some text between header 1 and 2
    
    ## Header 2<a name="header-2></a>
    Some text below header 2
"""
    parser = argparse.ArgumentParser(description=parser_help_text,formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("filename", help="Markdown file to add table of contents to")
    parser.add_argument("--skip_headers",
                        help="number of headers in the beginning of the file to not include in the toc (default: 0)",
                        default=0)
    args = parser.parse_args()

    filename = args.filename
    skip_headers = int(args.skip_headers)

    return filename, skip_headers

def main():
    mt = MdToc()
    input_lines = []
    
    filename, skip_headers = parse_command_line_arguments()
    
    f_in = open(filename, 'r')
    for line in f_in:
        input_lines.append(line.rstrip('\n'))
    f_in.close()
    
    output_lines = mt.add_toc(input_lines, skip_headers)
    
    f_out = open(filename, 'w')
    for line in output_lines:
        f_out.write(line + '\n')
    f_out.close()

            
if __name__ == '__main__':
    main()
