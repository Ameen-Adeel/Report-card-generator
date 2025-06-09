import statistics
import os
import json
from textwrap import dedent

# helper function to safely take user input and validate type + options
def check_value(user_input, type_, valid_options=None, allow_int_for_string = False, range_prompt = False):
    while True:
        try:
            choice = type_(input(user_input))

            if type_ == str and not allow_int_for_string:
                if choice.isdigit():
                    print("Please enter a proper string!")
                    continue

            if valid_options is not None and choice not in valid_options:
                if range_prompt and type_ == int:
                    print(f"\nPlease enter a value from {min(list(valid_options))} to {max(list(valid_options))}")
                    continue

                print(f"\nPlease enter a valid option from: {valid_options}")
                continue

            return choice
        
        except ValueError:
            print(f"Invalid output! Expected a integer")

# lets you add or remove subjects by number or name
def add_or_remove_subj(subjects):
    subj_num_dict = {}
    for subj in subjects:
        num, name = subj.split(".")
        subj_num_dict[num.strip()] = name.strip()

    add_or_remove = check_value("Would you like to ADD(a) or REMOVE(r) subject(s) : ", str, ('a', 'r')).lower().strip()

    if add_or_remove == "a":
        add_subj = check_value("Please provide the subject(s) you would like to add. Separate multiple subjects by commas: ", str)
        max_num = max(int(k) for k in subj_num_dict.keys())

        for subj in add_subj.strip().split(","):
            subj = subj.strip().title()
            if subj not in [name for name in subj_num_dict.values()]:
                max_num += 1
                subjects.append(f"{max_num}.{subj}")
                subj_num_dict[str(max_num)] = subj
                print(f"{subj} has been added to the subject list.")
            else:
                print(f"{subj} is already present in the subject list.")

    else:
        rem_input = check_value("Please provide the subject number(s) you would like to remove. Separate multiple numbers by commas: ", str, allow_int_for_string=True)
        rem_nums = [num.strip() for num in rem_input.strip().split(",") if num.strip().isdigit()]

        for num in rem_nums:
            if num in subj_num_dict:
                removed_name = subj_num_dict[num]
                print(f"\n{removed_name} has been removed from the subject list.")
            else:
                print(f"\nSubject number {num} not found.")

        # clean up subjects list and rebuild with new numbering
        subjects = [subj for subj in subjects if subj.split(".")[0].strip() not in rem_nums]
        subjects = [f"{i+1}.{subj.split('.')[1].strip()}" for i, subj in enumerate(subjects)]

        subj_num_dict = {}
        for subj in subjects:
            num, name = subj.split(".")
            subj_num_dict[num.strip()] = name.strip()

    return subjects, subj_num_dict

# turns percentage into grade
def grade_(percentage):
    if percentage >= 90:
        return 'A+'
    elif percentage >= 80:
        return 'A'
    elif percentage >= 70:
        return 'B'
    elif percentage >= 60:
        return 'C'
    elif percentage >= 50:
        return 'D'
    else:
        return 'F'

# calculates everything needed for the report
def calc(total_marks, obtained_marks, subjects):
    individual_perc = []
    for subj in subjects:
        perc = (obtained_marks[subj] / total_marks[subj]) * 100
        individual_perc.append(perc)

    individual_grades = []
    for perc in individual_perc:
        individual_grades.append(grade_(perc))

    total_percentage = (sum(obtained_marks.values()) / sum(total_marks.values())) * 100
    overall_grade = grade_(total_percentage)
    avg_marks = statistics.mean(obtained_marks.values())

    return individual_perc, individual_grades, total_percentage, overall_grade, avg_marks

# makes the final printable report string
def report_string(subjects, obtained_marks, total_marks,
                  individual_perc, individual_grades,
                  total_percentage, overall_grade, avg_marks,
                  name, class_):

    TEMPLATE = dedent("""
{dash}
{title:^73}
{dash}

Name   : {name}
Class  : {cls}

{dash}
{header_row}
{dash}
{subject_rows}{dash}
{overall_row}
{dash}
""")

    dash = "{:-<73}".format("")
    header_row = "{:<22}{:>12}{:>9}{:>9}{:>14}{:>7}".format(
        "SUBJECT", "OBTAINED", "TOTAL", "GRADE", "PERCENTAGE", "AVG"
    )

    subject_rows = ""
    for i, subj in enumerate(subjects):
        subject_rows += "{:<22}{:>12}{:>9}{:>9}{:>14.2f}{:>7}\n".format(
            subj,
            obtained_marks[subj],
            total_marks[subj],
            individual_grades[i],
            individual_perc[i],
            "N/A"
        )

    overall_row = "{:<22}{:>12}{:>9}{:>9}{:>14.2f}{:>7}".format(
        "OVERALL",
        sum(obtained_marks.values()),
        sum(total_marks.values()),
        overall_grade,
        total_percentage,
        avg_marks
    )

    return TEMPLATE.format(
        title="REPORT CARD",
        dash=dash,
        name=name.strip().upper(),
        cls=class_.strip(),
        header_row=header_row,
        subject_rows=subject_rows,
        overall_row=overall_row
    )

# saves the report card to a JSON file (named after student)
def save(report_card):
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    full_path = os.path.join(script_dir, f"{list(report_card.keys())[0]}_report_card.json")
    with open(full_path, "w") as f:
        json.dump(report_card, f)

# full report creation flow
def create_card():
    subj_edited = False
    subjects = ['1.English', '2.Urdu', '3.Pakistan Studies', '4.Maths', '5.Physics', '6.Chemistry', '7.Islamiat', '8.Computer Studies']

    print("\n📰----------Creating report card----------📰\n")
    student_name = check_value("Please enter your name: ", str).strip().title()
    student_class = str(check_value("Please enter your class (1-12): ", int, tuple(range(1, 13)), range_prompt=True)).strip()

    print("\nFollowing are the subjects for which you would be asked to provide the marks :  \n")
    for subj in subjects:
        print(subj)

    while True:
        subj_change = check_value("\nWould you like to add or remove any subject(y/n) : ", str, ('y', 'n'))
        if subj_change.strip().lower() == "y":
            subj_edited = True
            new_subjects, subj_num_dict = add_or_remove_subj(subjects)
            print("\nFollowing are the subjects for which you would be asked to provide the marks :  \n")
            for subj in new_subjects:
                print(subj)
        else:
            if not subj_edited:
                new_subjects = subjects
                subj_num_dict = {}
                for subj in new_subjects:
                    num, name = subj.split(".")
                    subj_num_dict[num.strip()] = name.strip()
            break

    subjects_total_marks = {subj: 100 for subj in new_subjects}

    while True:
        print("\nFollowing are the total marks of every subject for which all the calculations will be made :\n")
        for subj, marks in subjects_total_marks.items():
            print(f"\t{subj}   |   {marks}")
        print('\n')

        subjects_total_marks_change = check_value("Would you like to edit the subjects' total marks(y/n) : ", str, ('y', 'n'))
        if subjects_total_marks_change.strip().lower() == "y":
            print("\n✏️--------EDITING TOTAL MARKS--------✏️\n")
            edit_input = check_value("Please provide the subject number(s) whose total marks you would like to edit. Seperate multiple numbers by comma. Enter (a) if you intend to edit all the subjects' total marks : ", str, allow_int_for_string=True)

            if edit_input.strip().lower() == "a":
                for num in list(subj_num_dict.keys()):
                    print("\n New total marks for: \n")
                    new_marks = check_value(f"\t{subj_num_dict[num]} :  ", int, range(5, 101), range_prompt=True)
                    subjects_total_marks[f"{num}.{subj_num_dict[num]}"] = new_marks
            else:
                edit_nums = [num.strip() for num in edit_input.strip().split(',')]
                for num in edit_nums:
                    print("\n New total marks for: \n")
                    if num in subj_num_dict:
                        new_marks = check_value(f"\t{subj_num_dict[num]} :  ", int, range(5, 101), range_prompt=True)
                        subjects_total_marks[f"{num}.{subj_num_dict[num]}"] = new_marks
                    else:
                        print(f"\nSubject number {num} not found!")
        else:
            break

    subject_obtained_marks = {}
    print("\nCould you please provide the obtained marks for each subject : \n")
    for subj in new_subjects:
        subj_index = new_subjects.index(subj)
        marks = check_value(f"\t{subj}   :   ", int, range(0, (list(subjects_total_marks.values())[subj_index]) + 1), range_prompt=True)
        subject_obtained_marks[f'{subj}'] = marks

    individual_perc, individual_grades, total_percentage, overall_grade, avg_marks = calc(subjects_total_marks, subject_obtained_marks, new_subjects)

    print("\n")
    report_card = {student_name : report_string(new_subjects, subject_obtained_marks, subjects_total_marks, individual_perc, individual_grades, total_percentage, overall_grade, avg_marks, student_name, student_class)}
    print(report_card[student_name])

    save_permit = check_value("Would you like to save this report card(y/n) : ", str, ("y", "n"))
    if save_permit.strip().lower() == "y":
        save(report_card)

# shows saved report cards and allows user to choose one to view
def view():
    folder_path = os.path.dirname(os.path.abspath(__file__))
    all_files = os.listdir(folder_path)
    json_files = [f for f in all_files if f.endswith('.json') and not f.endswith('.py')]

    if json_files:
        print("\nFollowing are the saved report cards : \n")
        for idx, file in enumerate(json_files):
            student_name = file.replace("_report_card.json", "")
            print(f"\t{idx + 1}.{student_name}'s Report card")
        print("\n")
    else:
        print("\nThere are no saved report cards!")

    view_file = check_value("Which report card would you like to view. Please enter its number : ", int, range(1, len(json_files) + 1), range_prompt=True)
    idx = view_file - 1

    report_file_path = os.path.join(folder_path, json_files[idx])
    student = json_files[idx].replace("_report_card.json", "")

    with open(report_file_path, 'r') as f:
        report = json.load(f)
        print(report[student])

# starting prompt and main loop
def prompt(first_time=True):
    if first_time:
        print("\t📚  WELCOME TO THE REPORT CARD GENERATOR !!!  📚\n")

    print("\n1. Create new student report card")
    print("2. View saved report card")
    print("3. Exit")
    return check_value("Choose an option (1/2/3): ", int, (1, 2, 3))

first_time = True
while True:
    user_choice = prompt(first_time)
    first_time = False 
    if user_choice == 1:
        create_card()
    elif user_choice == 2:
        view()
    else:
        print("\nGOODBYE! THANKS FOR USING REPORT CARD GENERATOR...")
        exit()
