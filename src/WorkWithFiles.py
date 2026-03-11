import csv
import json
import os
print(os.getcwd())

with open('files/books.csv', newline='') as f:
    reader = csv.DictReader(f)
    books = list(reader)

not_needed_fields = 'Publisher'
for book in books:
    if not_needed_fields  in book:
        del book[not_needed_fields]



with open("files/users.json", newline='') as f:
     users = json.load(f)

fields_to_keep_users = ["name", "gender", "address", "age"]
users_final = [
    {key: user.get(key) for key in fields_to_keep_users} for user in users
]

for user in users_final:
    user["books"]= []

for i, book in enumerate(books):
    user_index = i % len(users_final)
    users_final[user_index]["books"].append(book)

with open("files/results.json", "w") as f:
    json.dump(users_final, f, indent = 2)


