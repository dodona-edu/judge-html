from validators import checks


def create_suite(content: str) -> checks.TestSuite:
    suite = checks.TestSuite(content)

    # Item 1: the HTML is valid
    ci_html_valid = checks.ChecklistItem("The HTML is valid.",
                                         suite.validate_html().or_abort()  # Abort all future tests if HTML is invalid
                                         )

    el_body = suite.element("body")
    el_table = el_body.get_child("table")

    # Item 2: there's a table
    ci_table_exists = checks.ChecklistItem("The body has a table.", [
        el_table.exists()
    ])

    # Item 3: table has a caption
    ci_table_has_caption = checks.ChecklistItem("The table has a caption.", el_table.has_child("caption"))

    # Item 4: caption is correct
    caption_content = "Hogwarts Faculties"
    ci_caption_is_correct = checks.ChecklistItem("The caption is correct.",
                                                 el_table.get_child("caption").has_content(caption_content)
                                                 )

    # Item 5: table has at least one row
    ci_table_has_rows = checks.ChecklistItem("The table has rows.", el_table.get_children("tr").at_least(1))

    # All table rows
    table_rows = el_table.get_children("tr")

    # Item 6: First row has a header, the header is correct
    header = ["Gryffindor", "Ravenclaw", "Hufflepuff", "Slytherin"]
    ci_table_header_is_correct = checks.ChecklistItem("The first row has a header with the required text.", [
        table_rows[0].has_child("th"),  # Check that the FIRST row is a header
        el_table.has_table_header(header)  # Check that the header matches up
    ])

    # Item 7: the second row is correct
    second_row = ["Hermione Granger", "Padma Patil", "Cedric Diggory", "Draco Malfoy"]
    ci_second_row_is_correct = checks.ChecklistItem("The second row contains the required data.",
                                                    table_rows[1].table_row_has_content(second_row)
                                                    )

    # Item 8: the third row is correct
    third_row = ["Harry Potter", "Luna Lovegood", "Hannah Longbottom", "Pansy Parkinson"]
    ci_third_row_is_correct = checks.ChecklistItem("The third row contains the required data",
                                                   table_rows[2].table_row_has_content(third_row))

    # Item 9: the fouth row is correct
    fouth_row = ["Ronald Weasley", "Cho Chang", "Susan Bones", "Gregory Goyle"]
    ci_fourth_row_is_correct = checks.ChecklistItem("The fourth row contains the required data",
                                                    table_rows[3].table_row_has_content(fouth_row)
                                                    )

    # Create checklist
    suite.checklist = [
        ci_html_valid,
        ci_table_exists,
        ci_table_has_caption,
        ci_caption_is_correct,
        ci_table_has_rows,
        ci_table_header_is_correct,
        ci_second_row_is_correct,
        ci_third_row_is_correct,
        ci_fourth_row_is_correct
    ]

    return suite
