import random
import pandas as pd

class Individual:
    def __init__(self, sex, birth_year, parents=None):
        self.sex = sex
        self.birth_year = birth_year
        self.age = 0  # Starts at age 0
        self.parents = parents  # List of parents (mother, father)

    def get_age(self, current_year):
        return current_year - self.birth_year

    def can_breed(self, sex, current_year):
        if sex == 'F':
            age = self.get_age(current_year)
            return age >= 2 and age <= 6
        else:
            age = self.get_age(current_year)
            return age <= 8

    def is_alive(self, current_year):
        age = self.get_age(current_year)
        return age <= 8


class Population:
    def __init__(self):
        # Start with 2 females and 3 males in 2018
        self.individuals = [
            Individual(sex='F', birth_year=2018),  # Female 1
            Individual(sex='F', birth_year=2018),  # Female 2
            Individual(sex='M', birth_year=2018),  # Male 1
            Individual(sex='M', birth_year=2018),  # Male 2
            Individual(sex='M', birth_year=2018),  # Male 3
        ]
        self.population_data = []  # To keep track of all individuals' data

    def get_females(self, current_year):
        return [ind for ind in self.individuals if ind.sex == 'F' and ind.can_breed('F', current_year)]

    def get_males(self, current_year):
        return [ind for ind in self.individuals if ind.sex == 'M' and ind.can_breed('M', current_year)]

    def breed(self, current_year):
        females = self.get_females(current_year)
        males = self.get_males(current_year)

        # We need two pairs to breed
        pairs = []
        for _ in range(2):
            if females and males:
                female = random.choice(females)
                male = random.choice(males)
                pairs.append((female, male))
                females.remove(female)
                males.remove(male)

        # Produce 2 children for each pair
        children = []
        for female, male in pairs:
            # Child sex ratio: 2 females to 3 males
            for _ in range(2):  # Each pair produces 2 children
                sex = 'F' if random.randint(1, 3) <= 2 else 'M'
                child = Individual(sex, birth_year=current_year, parents=[female, male])
                children.append(child)

                # Add the child's data to population_data
                self.population_data.append({
                    'Sex': child.sex,
                    'Birth Year': child.birth_year,
                    'Parents': f"Female {female.birth_year}-{female.sex}, Male {male.birth_year}-{male.sex}"
                })

        # Add children to population (they will start breeding in 2 years)
        self.individuals.extend(children)

    def remove_dead(self, current_year):
        self.individuals = [ind for ind in self.individuals if ind.is_alive(current_year)]

    def get_population_size(self):
        return len(self.individuals)

    def get_population_data(self):
        # Return population data for all individuals
        for individual in self.individuals:
            if not any(record['Birth Year'] == individual.birth_year and record['Sex'] == individual.sex for record in self.population_data):
                self.population_data.append({
                    'Sex': individual.sex,
                    'Birth Year': individual.birth_year,
                    'Parents': 'None'
                })
        return self.population_data


def run_simulation():
    population = Population()
    year = 2018
    target_population = 40

    while population.get_population_size() < target_population:
        year += 1
        print(f"Year: {year}, Population size: {population.get_population_size()}")

        # Remove individuals who are dead
        population.remove_dead(year)

        # Breed new individuals
        population.breed(year)

    print(f"Target population of {target_population} reached in year {year}!")

    # After the simulation, generate the Excel file
    population_data = population.get_population_data()
    df = pd.DataFrame(population_data)

    # Save the DataFrame to an Excel file
    df.to_excel("population_data.xlsx", index=False)
    print("Excel file 'population_data.xlsx' generated!")

if __name__ == "__main__":
    run_simulation()
