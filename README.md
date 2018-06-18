# mdtoc - Markdown Table of Contents

mdtoc will create a table of contents and insert below the header named Contents. Any existing lines in the Contents section will be removed. An error message will be emitted if no Contents header is found in the input file.

mdtoc can only handle Atx-style headers (see https://daringfireball.net/projects/markdown/syntax#header).

Example:

    ## This is a atx-style header

mdtoc cannot handle "closed" atx-style headers or headers using the underline syntax: 

    ## Closed header ##

    Underlined header
    =================

Example:

    $ python3 mdtoc.py article.md

article.md before running mdtoc:

    # Contents
    # Header 1
    Some text between header 1 and 2
    
    ## Header 2
    Some text below header 2

article.md after running mdtoc:

    # Contents<a name="contents"></a>
    
    * [Contents](#contents)
    * [Header 1](#header-1)
        * [Header 2](#header-2)

    # Header 1<a name="header-1"></a>
    Some text between header 1 and 2
    
    ## Header 2<a name="header-2></a>
    Some text below header 2
