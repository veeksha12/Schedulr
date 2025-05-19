def create_study_prompt(courses, hours_available):
    prompt = f"I have {hours_available} hours to study today.\nHere are my courses:\n"
    for c in courses:
        prompt += f"- {c.name}: Current {c.current_grade}/10, Target {c.target_grade}/10\n"
    prompt += (
        "\nMake a detailed, prioritized schedule for today based on these goals. "
        "Mention what to study in each time block, and focus more on subjects with the biggest grade gaps."
    )
    return prompt