# The amount of respins
respins = 5

# The probability distribution of the items
prob_dash       = 0.28
prob_coin       = 0.3
prob_coin_stack = 0.1
prob_double     = 0.09
prob_snake      = 0.1
prob_fishnet    = 0.04
prob_clover     = 0.01
prob_crown      = 0.08

probabilities = {"dash"       : prob_dash,
                 "coin"       : prob_coin,
                 "coin_stack" : prob_coin_stack,
                 "double"     : prob_double,
                 "snake"      : prob_snake,
                 "fishnet"    : prob_fishnet,
                 "clover"     : prob_clover,
                 "crown"      : prob_crown}



def calculate_payout(state):
  coins       = state.count("coin")
  coin_stacks = state.count("coin_stack")
  times2      = state.count("double")
  snakes      = state.count("snake")
  clovers     = state.count("clover")
  crowns      = state.count("crown")

  if crowns == 4:
      return 100
  elif coins == 4:
      return 5
  elif coin_stacks == 4:
      return 15
  elif snakes > 0:
    if "fishnet" in state:
      return snakes * 3 * 2**times2
    else:
      return 0

  current_winnings = 0
  current_winnings += clovers * 10
  if coins == 3:
    current_winnings += 3
  if coin_stacks == 3:
    current_winnings += 9

  return current_winnings * 2**times2

def get_all_states():

  all_states = {}

  for first_result in probabilities:
    for second_result in probabilities:
      for third_result in probabilities:
        for fourth_result in probabilities:
          state = [first_result, second_result, third_result, fourth_result]
          state.sort()
          state = tuple(state)
          probability = probabilities[first_result] * \
                        probabilities[second_result] * \
                        probabilities[third_result] * \
                        probabilities[fourth_result]

          # Check if we already had this state
          if state in all_states:
            all_states[state] += probability
          else:
            all_states[state] = probability

  return all_states

def get_respin_states(start_state, respin_index):

  respin_states = {}

  state_list = list(start_state)
  del state_list[respin_index]

  for respin_result, probability in probabilities.items():
    state = tuple(state_list + [respin_result])

    # No possibility for collisions
    respin_states[state] = probability

  return respin_states

def calculate_expected_gain(state, respin_index, respins_remaining):

  respin_states = get_respin_states(start_state  = state,
                                    respin_index = respin_index)

  expected_gain = -1
  for state, probability in respin_states.items():
    expected_gain += probability * choose_step(state             = state,
                                               respins_remaining = respins_remaining)

  return expected_gain

def calculate_expected_gain_start(respins_remaining):

  all_states = get_all_states()

  # Gain for spending 1 coin to pull the trigger
  expected_gain = -1
  for state, probability in all_states.items():
    expected_gain += probability * choose_step(state             = state,
                                               respins_remaining = respins_remaining)

  return expected_gain

memoisation = {}
def choose_step(state, respins_remaining):

  # Memoisation to reduce the redundant calculations
  state_sorted = list(state)
  state_sorted.sort()
  state_sorted = tuple(state_sorted)
  if respins_remaining in memoisation:
    if state_sorted in memoisation[respins_remaining]:
      return memoisation[respins_remaining][state_sorted]
  else:
    memoisation[respins_remaining] = {}

  # Choose not to continue
  best_gain = calculate_payout(state_sorted)

  # Respin the wheels
  if respins_remaining > 0:
    respin_symbols = set()
    for i in range(4):
      if state_sorted[i] not in respin_symbols:
        gain = calculate_expected_gain(state             = state_sorted,
                                       respin_index      = i,
                                       respins_remaining = respins_remaining - 1)
        best_gain = max(best_gain, gain)
        respin_symbols.add(state_sorted[i])

  memoisation[respins_remaining][state_sorted] = best_gain

  return best_gain

def choose_step_start(starting_respins):

  # Gain for spending 1 coin to pull the trigger
  best_gain = calculate_expected_gain_start(starting_respins)

  # Gain for not pulling the trigger
  best_gain = max(best_gain, 0)

  return best_gain

def get_user_input(prompt, allowed_inputs):

  user_input = input(prompt)

  while user_input not in allowed_inputs:
    print(f"Input not recognised. Please choose from the allowed list {allowed_inputs}")
    user_input = input(prompt)

  return user_input

def interactive_choose(state, respins_remaining):

  # Choose not to continue
  no_spin_gain = calculate_payout(state)

  # Respin the wheels
  spin_gain = []
  for i in range(4):
    gain = calculate_expected_gain(state             = state,
                                   respin_index      = i,
                                   respins_remaining = respins_remaining - 1)
    spin_gain.append(gain)

  commands = [f"respin_{i + 1}" for i in range(4)] + ["stop"]

  print("##########################")
  print("### Choose your action ###")
  print("##########################")
  print(f"Respins remaining: {respins_remaining}")
  print()

  for i in range(4):
    print(f"Respin wheel {i + 1}:")
    print(f"  Expected gain: {spin_gain[i]} coins")
    print(f"  Input command: {commands[i]}")
    print()

  print("Do not respin and cash in the payout:")
  print(f"  Expected gain: {no_spin_gain} coins")
  print(f"  Input command: {commands[-1]}")
  print()

  recommendation = commands[-1]
  best_gain = no_spin_gain
  for i in range(4):
    if spin_gain[i] > best_gain:
      best_gain = spin_gain[i]
      recommendation = commands[i]

  print(f"Recommended action is: {recommendation}")
  print()

  command = get_user_input(prompt         = "Please select your action: ",
                           allowed_inputs = commands)

  print()

  if command == commands[-1] or respins_remaining == 1:
    print("Thanks for playing!")
  else:
    prompt = "What was the result of the respin: "
    respin_result = get_user_input(prompt         = prompt,
                                   allowed_inputs = probabilities.keys())

    respin_index = commands.index(command)
    state = list(state)
    state[respin_index] = respin_result
    state = tuple(state)

    print()

    interactive_choose(state = state,
                       respins_remaining = respins_remaining - 1)

def interactive_choose_start(starting_respins):

  # Gain for spending 1 coin to pull the trigger
  spin_gain = calculate_expected_gain_start(starting_respins)

  # Gain for not pulling the trigger
  no_spin_gain = 0

  commands = ["pull", "stop"]

  print("##########################")
  print("### Choose your action ###")
  print("##########################")
  print("Pull the lever:")
  print(f"  Expected gain: {spin_gain} coins")
  print(f"  Input command: {commands[0]}")
  print()
  print("Do not pull the lever:")
  print(f"  Expected gain: {no_spin_gain} coins")
  print(f"  Input command: {commands[1]}")
  print()

  if spin_gain > no_spin_gain:
    recommendation = commands[0]
  else:
    recommendation = commands[1]

  print(f"Recommended action is: {recommendation}")
  print()

  command = get_user_input(prompt         = "Please select your action: ",
                           allowed_inputs = commands)

  print()

  if command == commands[-1] or starting_respins == 0:
    print("Thanks for playing!")
  else:
    prompt = "What was the result of the first wheel: "
    first_result = get_user_input(prompt         = prompt,
                                  allowed_inputs = probabilities.keys())
    prompt = "What was the result of the second wheel: "
    second_result = get_user_input(prompt         = prompt,
                                   allowed_inputs = probabilities.keys())
    prompt = "What was the result of the third wheel: "
    third_result = get_user_input(prompt         = prompt,
                                  allowed_inputs = probabilities.keys())
    prompt = "What was the result of the fourth wheel: "
    fourth_result = get_user_input(prompt         = prompt,
                                   allowed_inputs = probabilities.keys())

    print()

    state = (first_result, second_result, third_result, fourth_result)
    interactive_choose(state = state,
                       respins_remaining = starting_respins)


print(f"Running Blue Prince casino game with {respins} number of respins")
print("--------------------------------------------------------")
print()
interactive_choose_start(respins)
