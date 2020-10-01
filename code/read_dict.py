import ast
file = open("translated_seed_list_complete.txt", "r")


contents = file.read()

dictionary = ast.literal_eval(contents)


file.close()


print(dictionary['hebrew'])