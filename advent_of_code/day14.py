from pathlib import Path
import re
from collections import defaultdict
from math import floor,ceil
import numpy as np


# need to sort all reactions with a level number which is a distance away from ore
# iterate through reactions, for every one that is only who's reactant set is a subset of the already produced materials gets assigned a number

class Refinery():
    # a refinery object keeps track of all reactions possible, breaks down components into their base parts
    # has a surplus inventory to keep track of materials created by the reaction but not used
    # need to load all reaction recipes into the refinery


    def __init__(self,reactions, verbose=False):
        self._verbose=verbose
        self._reactions=reactions   #all reactions that the refinery can process
        self._raw_materials = [material for _, material in
                               sorted([(item.level, key) for key, item in reactions.items()],
                                      key=lambda pair: pair[0],reverse=True)]  # raw materials reverse sorted by distance from ore
        self.reset()

    @property
    def raw_materials(self):
        return self._raw_materials

    def set_target(self,target_material,quantity):
        #loads the desired material into teh required_materials dictionary
        self._required_materials[target_material]=quantity

    def reset(self):
        #reset the reactor to its initial state
        self._surplus = defaultdict(int)  # dict that keeps track of surpluses from the reaction
        self._required_materials = defaultdict(int)  # dict that keeps track of materials required for reaction

    def run_reactor(self):
        # searches through the required materials for nonzero entries
        # if it finds a material that needs to be broken down it determines the minimum submaterials needed for a reaction
        # puts the excess in surplus, and puts the required ones in required materials tab
        for material in self._raw_materials:
            to_produce=self._required_materials[material]+self._surplus[material]    #how much needs to be created
            if to_produce!=0:
                if self._verbose: print("need to produce {} {}".format(to_produce,material))
                required_reactions=to_produce/self._reactions[material].min_quantity  #how many reactions we need and it better be an integer number or the math is off somewhere
                for subcomponent,quantity in self._reactions[material].recipe:
                    if self._verbose:
                        print("\trecipe requires {} {}, have {} in surplus".format(required_reactions * quantity,
                                                                                   subcomponent,
                                                                                   self._surplus[subcomponent]))
                    required_subcomponent=required_reactions*quantity   #how many subcomponents are needed to produce the reactant
                    self._required_materials[subcomponent]+=required_subcomponent
                    subcomponent_deficit=required_subcomponent-self._surplus[subcomponent]  #how much we still need, positive is we need material, negative is we have enough
                    if subcomponent_deficit>0: #if we need more subcomponents for the reaction
                        subcomponent_reactions=ceil(subcomponent_deficit/self._reactions[subcomponent].min_quantity)
                        #perform the breakdown and put the remainder in surplus
                        self._surplus[subcomponent]=(self._reactions[subcomponent].min_quantity*subcomponent_reactions-subcomponent_deficit)
                    else:
                        self._surplus[subcomponent]=-subcomponent_deficit
                        #update the surplus to the amound remaining after consuming the reaction
        #after the reaction return how much ore is required to perform the conversion
        return self._required_materials['ORE']



class Reaction():
    def __init__(self,output,min_quantity,recipe,level=None):
        self._output=output # The string name of what is produced by this reaction
        self._min_quantity=min_quantity # Minimum production quantity for the reaction
        self._recipe=recipe # A list of tuples that have the ingredients and quantity needed to perform the reaction
        self.level=level

    def __str__(self):
        #string representation of reaction
        return ''.join([
            ','.join(["{} {}".format(ingredient[1],ingredient[0]) for ingredient in self._recipe]),
            "=> {} {}".format(self._min_quantity,self._output)])

    @property
    def name(self):
        return self._output

    @property
    def min_quantity(self):
        return self._min_quantity

    @property
    def recipe(self):
        return self._recipe

def populate_reaction_level(reactions):
    reaction_level=1
    reaction_set={"ORE"}   #the reaction set starts with Ore because infinite ore is available
    level_assignment_complete=False
    while not level_assignment_complete:
        level_n_reactions = []
        for key,reaction in reactions.items():
            ingredients={ingredient for ingredient,_ in reaction.recipe}
            if ingredients.issubset(reaction_set) and reaction.level==None:
                #if the ingredient list is a subset and the reaction level is not currently assigned
                level_n_reactions.append(key)   #add the key to the next level of subsets
                reaction.level=reaction_level   #set the appropriate reaction level
        reaction_level+=1   #increment the reaction level
        reaction_set.update(level_n_reactions)  #add the previous level reactions to the set
        if not level_n_reactions:   #if we haven't added any new reactions since iteration exit
            level_assignment_complete=True

def parse_component_string(component):
    #returns a tuple of the component and how much is needed
    quantity,type=component.split()
    return type,int(quantity)

def import_reactions(file_path):
    reactions={"ORE" : Reaction("ORE",1,[],level=0)}    # reaction list always starts with Ore that can be synthesized infinitely
    with open(file_path) as file:
        for line in file.readlines():
            components,result=line.split("=>")
            regex_pattern="[0-9]+ [A-Z]+" #pattern is one or more numbers, a space, and one or more letters
            recipe=[tuple(parse_component_string(component)) for component in re.findall(regex_pattern,components)]
            output,min_quantity=parse_component_string(result)
            reactions[output]=Reaction(output,min_quantity,recipe)  #make a new reaction and add it to the dictionary, key is name of output
    populate_reaction_level(reactions)
    return reactions    #return the reactions


def puzzle_part_a(refinery):
    refinery.set_target("FUEL", 1)
    required_ore = refinery.run_reactor()
    print("{} Ore is required for reaction".format(required_ore))

def puzzle_part_b(refinery):
    fuel_test_cases=[round(10**(j/100)) for j in range(600,700)]
    for fuel_amount in fuel_test_cases:
        refinery.reset()    #reset the reactor
        refinery.set_target("FUEL",fuel_amount)  #try to
        required_ore = refinery.run_reactor()
        if required_ore>1000000000000:   #if it requires more than a trillion ore
            print("{} Fuel is Too Much".format(fuel_amount))
        else:
            print("{} Fuel is Too Little".format(fuel_amount))
    ore_threshold_tripped=False
    fuel=1949845    #how much fuel to start with based on search above
    while not ore_threshold_tripped:
        fuel+=1
        refinery.reset()  # reset the reactor
        refinery.set_target("FUEL", fuel)
        required_ore = refinery.run_reactor()
        if required_ore > 1000000000000:
            ore_threshold_tripped=True
    print("One Trillion ore can produece {} Fuel".format(fuel-1))



def main():
    #import reactions into refinery
    puzzle_input_path=Path("puzzle_inputs") / "day14_input.txt"
    reactions=import_reactions(puzzle_input_path)
    refinery=Refinery(reactions,verbose=False)
    puzzle_part_a(refinery)
    refinery.reset()
    puzzle_part_b(refinery)



if __name__=="__main__":
    main()