import csv
import sys
import time

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def generate_neighbors_without_source(neighbor_set, person_id):
    """
    Returns the set of movies and their stars not
    including the person id given to produce the set.
    """
    sanitized_neighbors = set()
    for neighbor in neighbor_set:
        if str(person_id) not in neighbor:
            sanitized_neighbors.add(neighbor)
    return sanitized_neighbors


def generate_goal_states(neighbor_set, person_id):
    """
    Returns only the set of movies starring
    the person id given to produce the set.
    """
    goal_states = set()
    for neighbor in neighbor_set:
        if str(person_id) in neighbor:
            goal_states.add(neighbor)
    return goal_states


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    explored_states = set()
    goal_state_node = None
    solution_path = None
    solution_length = 9999  # setting maximum value to use when returning shortest path
    possible_paths = QueueFrontier()
    neighbors = generate_neighbors_without_source(neighbors_for_person(source), source)
    goal_states = generate_goal_states(neighbors_for_person(target), target)

    # Add nodes to frontier
    for neighbor in neighbors:
        possible_paths.add(Node(
            state=neighbor,
            parent=(None, str(source)),
            action=[neighbor]
        ))
    
    print("Processing...")
    start = time.process_time()
    # Loop through nodes in frontier
    while not possible_paths.empty():
        # Remove next node
        node = possible_paths.remove()
        # Add node's state to explored states set
        explored_states.add(node.state)
        # Check if frontier is empty
        if possible_paths.empty():
            print(f"Frontier is empty! Processing finished in: {time.process_time() - start} seconds.")
            return None
        # Add resulting nodes from current node
        node_person = node.state[1]
        neighbors = generate_neighbors_without_source(
            neighbors_for_person(node_person), node_person)
        for neighbor in neighbors:
            # Return path if goal state in frontier
            for state in goal_states:
                if possible_paths.contains_state(state):
                    goal_state_node = [node for node in possible_paths.frontier if node.state == state][0]
                    if len(goal_state_node.action) < solution_length:
                        solution_length = len(goal_state_node.action)
                        solution_path = goal_state_node.action
                    else:
                        print(f"Goal state found! Processing finished in: {time.process_time() - start} seconds.")
                        return solution_path
            # Otherwise, add neighbor if not in explored states or frontier
            if neighbor not in explored_states and \
                    neighbor not in [node.state for node in possible_paths.frontier]:
                possible_paths.add(Node(
                    state=neighbor,
                    parent=node.state,
                    action=node.action + [neighbor]  # Save previous actions list and add neighbor
                ))


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
