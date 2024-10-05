"""Module to generate fake .txt file in current directory"""

from faker import Faker

fake = Faker()
filename = fake.file_name(extension='txt')
text = fake.text(max_nb_chars=10000)
with open(filename, 'w+') as f:
    f.write(text)
print('Done!')
print(f'{filename}.txt generated.')
