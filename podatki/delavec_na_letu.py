import random

seznam_delavcev = []
seznam_imen = ["Raheem Derrick", "Ashley Hassan", "Tomas Kirk", "April Charlton", "Rocco Herrera", "Tai Marshall", "Johnathon Perry", "Stan Santana", "Isabelle North", "Kelly Blanchard", "Isaiah Walton", "Harper-Rose Hays", "Jardel Reid", "Shaunna Horton", "Lexi-May Kearns", "Carlton Arias", "Keyaan Andrews", "Amrita Delgado", "Ryker David", "Kendrick Conner", "Herbie Davenport", "Gabija Guerrero", "Maia Wyatt", "Dillan Hail", "Percy Turner", "Guy Hansen", "Corrina Barker", "Iman Kaye", "Faye Rubio", "Arjan Ingram", "Alanna Atkinson", "Romana Adkins", "Dolores Pitts", "Julian Deleon", "Teodor Knott", "Reagan Riggs", "Kavita Arellano", "Tia Reynolds", "Kaya Waters", "Corben Tyler", "Craig Alvarado", "Danielius Davey", "Mariya Gardiner", "Shyla Neale", "Constance Mcintyre", "Helena Brewer", "Tarun Ryan", "Sama Crane", "Inez Copeland", "Ami Espinoza", "Billy Wilks", "Anton Guerra", "Beauden Chavez", "Chenai Tierney", "Moses Navarro", "Lillie Parkes", "Koa Worthington", "Sharna Whitney", "Ayub Guest", "Chanel Richardson", "Zena Gibson", "Pearl Cotton", "Sherri Dejesus", "Tahlia Lynn", "Jac Adamson", "Sarah Gallagher", "Hunter Begum", "Vivek Bloggs", "Camron Barr", "Abbi Landry", "Neal Merrill", "Arbaaz Sloan", "Thea Woodard", "Roy Day", "Gracie-May Gates", "Saara Skinner", "Jeff Cobb", "Zack Wright", "Harriet Beaumont", "Anwen Yates", "Raihan Rawlings", "Persephone Dunne", "Phoenix Evans", "Brian Deacon", "Theodora Boyle", "Brooke Mcnally", "Bree Sutherland", "Kaia Weber", "Shayla Bishop", "Lorena Henson", "Manuel Sutton", "Nicky Stamp", "Greyson Yoder", "Jaidon Richmond", "Demi-Lee Davidson", "Kristina Vance", "Ayah Fox", "Tabitha Preston", "Mikey Vaughn", "Lydia Morrow"]
for id in range(100):
    ime = seznam_imen[id]
    if id % 10 == 0:
        delo = 'pilot'
    elif id % 10 == 1:
        delo = 'kopilot'
    else:
        delo = 'posadka'
    starost = random.randrange(22, 60)
    ekipa = id // 10
    seznam_delavcev.append(f"insert into delavec_na_letu (id, ime, delo, starost, ekipa) values ({id}, {ime}, {delo}, {starost}, {ekipa})")

for i in seznam_delavcev:
    print(i)