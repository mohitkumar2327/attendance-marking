# Excel Import Template Creation Script

import pandas as pd

df = pd.DataFrame(columns=[
    "name", "roll_no", "department", "year",
    "email", "parent_email", "type"
])

# Sample data
df.loc[0] = ["John Doe",   "CS001", "Computer Science", "1st Year", "john@email.com",  "parent1@email.com", "student"]
df.loc[1] = ["Jane Smith", "CS002", "Computer Science", "2nd Year", "jane@email.com",  "parent2@email.com", "student"]
df.loc[2] = ["Mr. Kumar",  "EMP001","Administration",   "N/A",      "kumar@school.com","",                  "employee"]
df.loc[3] = ["Ms. Priya",  "EMP002","Teaching Staff",   "N/A",      "priya@school.com","",                  "employee"]

df.to_excel("students_template.xlsx", index=False)
print("Template created: students_template.xlsx")
print("Fill this file and upload it via the web app.")