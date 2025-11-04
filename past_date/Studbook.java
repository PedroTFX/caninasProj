// the population stats with 5 individuals that are the breeders 2 females and 3 males
// the goal is get to 40 indiuduals

// restrictions
// avoid inbreeding parents brothers and cousins are not allowed to breed
// there are 2 couples per year each couple has 2 childs, assume that the parents are the most dif geneticly,
// they can only enter in the breeder poll after 2 years of age
// females cant breed after 6 years of age
// they die after 8 years of age
// the sex ration is 2females per 3males
// the child as a 2/3 sex ratio
// the first generation 2018 dont breed till 2020



public class Studbook {
    public static void main(String[] args) {
        // create the population
        Population population = new Population(5, 2, 3);
        // create the breeder poll
        BreederPoll breederPoll = new BreederPoll();
        // create the year
        Year year = new Year(2018);
        // create the studbook
        Studbook studbook = new Studbook(population, breederPoll, year);
        // start the simulation
        studbook.start();
    }

    private Population population;
    private BreederPoll breederPoll;
    private Year year;

    public Studbook(Population population, BreederPoll breederPoll, Year year) {
        this.population = population;
        this.breederPoll = breederPoll;
        this.year = year;
    }

    public void start() {
        while (population.getSize() < 40) {
            // check if the year is 2020
            if (year.getYear() == 2020) {
                // add the breeder to the breeder poll
                breederPoll.addBreeder(population.getBreeder());
            }
            // check if the year is 2022
            if (year.getYear() == 2022) {
                // add the breeder to the breeder poll
                breederPoll.addBreeder(population.getBreeder());
            }
            // check if the year is 2024
            if (year.getYear() == 2024) {
                // add the breeder to the breeder poll
                breederPoll.addBreeder(population.getBreeder());
            }
            // check if the year is 2026
            if (year.getYear() == 2026) {
                // add the breeder to the breeder poll
                breederPoll.addBreeder(population.getBreeder());
            }
            // check if the year is 2028
            if (year.getYear() == 2028) {
                // add the breeder to the breeder poll
                breederPoll.addBreeder(population.getBreeder());
            }
            // check if the year is 2029
            if (year.getYear() == 2029) {
                // add the breeder to the breeder poll
                breederPoll.addBreeder(population.getBreeder());
            }


