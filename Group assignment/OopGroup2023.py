from abc import ABC, abstractmethod

import pygame
import threading
import time


def game_timer(duration, flag, remaining_time):
    start_time = time.time()
    while time.time() - start_time < duration:
        time.sleep(0.1)  # Check every 0.1 seconds
        remaining_time[0] = duration - (time.time() - start_time)
    flag[0] = True


class Loggable:
    def __init__(self):
        self.__logs = []

    @property
    def logs(self):
        return self.__logs

    def log(self, message):
        if isinstance(message, str):
            self.__logs.append(message)


class PlayerStats:
    def __init__(self):
        self.clues_found = 0
        self.decisions_made = []
        self.start_time = time.time()
        self.end_time = None

    def add_clue_found(self):
        self.clues_found += 1

    def add_decision(self, decision):
        self.decisions_made.append(decision)

    def set_end_time(self):
        self.end_time = time.time()

    def get_time_taken(self):
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    def display_summary(self):
        print("\nGame Summary:")
        print(f"Total Clues Found: {self.clues_found}")
        print(f"Decisions Made: {self.decisions_made}")
        print(f"Time Taken: {self.get_time_taken():.2f} seconds")


class CrimeScene:
    def __init__(self, location):
        self.location = location
        self.__clues = []
        self.__investigated = False

    @property
    def investigated(self):
        return self.__investigated

    @investigated.setter
    def investigated(self, value):
        self.__investigated = value

    def add_clue(self, clue):
        self.__clues.append(clue)

    def review_clues(self):
        return self.__clues


class Character(ABC):
    def __init__(self, name, dialogue):
        self._name = name
        self._dialogue = dialogue
        self._interacted = False

    def __str__(self):
        return f"{self._name}"

    def __eq__(self, other):
        if isinstance(other, Character):
            return self._name == other._name
        return False

    def __lt__(self, other):
        if isinstance(other, Character):
            return self._name < other._name
        return False

    @abstractmethod
    def perform_action(self):
        pass

    def interact(self):
        if not self._interacted:
            interaction = f"{self._name}: {self._dialogue}"
            self._interacted = True
        else:
            interaction = f"{self._name} is no longer interested in talking."

        return interaction


class Suspect(Character):
    def __init__(self, name, dialogue, alibi):
        super().__init__(name, dialogue)
        self._alibi = alibi

    def provide_alibi(self):
        return f"{self._name}'s Alibi: {self._alibi}"

    def perform_action(self):
        return "\033[97mMr. Ireland nervously shifts his dark suit and avoids eye contact.\033[0m"


class Witness(Character):
    def __init__(self, name, dialogue, observation):
        super().__init__(name, dialogue)
        self._observation = observation

    def share_observation(self):
        return f"{self._name}'s Observation: {self._observation}"

    def perform_action(self):
        return f"\033[97mWitness {self._name} speaks hurriedly and glances around anxiously.\033[0m"


class NPC(Character):
    def perform_action(self):
        return f"\033[97m{self._name} decides to hang around and see what will happen.\033[0m"

    def interact(self):
        super().interact()
        return "\nHe is a terrible leader and will ruin the our diplomatic relations between our nations but I know nothing!"

    def interact(self):
        if not self._interacted:
            interaction = f"{self._name}: {self._dialogue}"
            self._interacted = True
        else:
            interaction = f"{self._name} is no longer interested in talking."

        return interaction


class Game:
    def __init__(self):
        self.player_stats = PlayerStats()
        self.__logger = Loggable()
        self.__error_logger = Loggable()
        self.__running = True
        self.__game_started = False
        self.__characters_interacted = False
        self.__npcs_interacted = False
        self.remaining_time = [0]  # Shared variable for remaining time
        self.timer_flag = [False]  # Flag to check if time is up

        self.__crime_scene = CrimeScene("First Carriage of Train")
        self.__suspect = Suspect("Mr. Ireland", "I was asleep in the second carriage for the evening.",
                                 "Confirmed by Mr Spain.")
        self.__witness = Witness("Ms. England", "I saw someone run towards carriage 3 after the incident.",
                                 "Suspicious figure in dark clothing.")
        self.__doors = ["\033[92mCarriage 1\033[0m", "\033[33mCarriage 2\033[0m",
                        "\033[91mCarriage 3\033[0m"]  # different colours for each carriage making it more grahpicall appealing
        self.__doors_checker = [False, False, False]
        # Sound effect files
        self.background_sound_file = "background.mp3"
        self.background_sound_thread = threading.Thread(target=self.play_background_sound)
        self.background_sound_file = "background1.mp3"
        self.trumpets_sound_file = "trumpets.mp3"
        self.womp_sound_file = "womp.mp3"

        # Initialize pygame
        pygame.init()

    def play_background_sound(self):
        pygame.mixer.music.load(self.background_sound_file)
        pygame.mixer.music.play(-1)  # Play in a loop

    def play_sound_effect(self, sound_file):
        sound = pygame.mixer.Sound(sound_file)
        sound.play()

    def stop_background_sound(self):
        pygame.mixer.music.stop()
        self.__running = False
        self.background_sound_thread.join()

    def get_logs(self):
        return self.__logger.logs

    def get_error_logs(self):
        return self.__error_logger.logs

    def title_screen(self):
        pygame.mixer.music.load("background.mp3")
        pygame.mixer.music.play()
        print("\033[92mWelcome to 'The Train Murder Mystery'")
        print("Created by Derry, Noah, Pierce, Niall, Ronan and Patrick.")
        print("Your expertise is needed to solve a complex case and unveil the truth.\033[0m")

        input("Press Enter to start the game")

        return True

    def run(self):
        timer_flag = [False]  # Flag to check if time is up
        timer_thread = threading.Thread(target=game_timer, args=(300, timer_flag, self.remaining_time))
        timer_thread.start()  # Start the timer thread
        self.timer_started = True
        timer_thread = threading.Thread(target=game_timer, args=(300, self.timer_flag, self.remaining_time))
        timer_thread.start()

        self.__logger.log("Game started")
        print("\033[92mWelcome to 'The Train Murder Mystery'")
        print("You are about to embark on a thrilling adventure as an agent of Interpol.")
        print("Your expertise is needed to solve a complex case and unveil the truth.\033[0m")

        self.background_sound_thread.start()

        while self.__running:
            self.display_remaining_time()  # Display the remaining time

            if timer_flag[0]:  # Check if time is up
                print("Time's up! The game has ended.")
                break  # End the game

            try:
                self.update()
            except ValueError as ve:
                self.__error_logger.log(f"Error found:\n{ve}.")
            except Exception as e:
                self.__error_logger.log(f"Unexpected error from run():\n{e}.")
                print("Unexpected caught error during running of the Game. We continue playing...")
            else:
                self.__logger.log("Successfully updating")
            finally:
                self.player_stats.set_end_time()  # Set the end time when the game loop ends
                self.__logger.log("---")


    def display_remaining_time(self):
        if self.timer_flag[0] and self.remaining_time[0] <= 0:
            print(
                "\033[31mNo time remaining. You failed to make an arrest before the train reached its destination and the culprit has gone free.\033[0m")
        elif self.timer_started:
            print(f"Time remaining: {self.remaining_time[0]:.2f} seconds")

    def update(self):
        self.__logger.log("I'm updating")

        if not self.__game_started:
            player_input = input("Press 'q' to quit or 's' to start: ")
            if player_input.lower() == "q":
                self.__running = False
            elif player_input.lower() == "s":
                self.__game_started = True
                self.start_game()
            else:
                print("\033[91mInvalid User Entry\033[0m")
                raise ValueError("Incorrect user entry.")
        else:
            player_input = input(
                "\033[97mPress 'q' to quit, 'a' to continue with arrest, 'i' to interact, "
                "'e' to examine crime scene, 'r' to review clues or 'c' to choose a "
                "carriage: \033[0m")

            self.__logger.log(f"Player input is {player_input}.")

            if player_input.lower() == "q":
                self.__running = False
            elif player_input.lower() == "a":
                self.continue_game()
            elif player_input.lower() == "i":
                try:
                    self.interact_with_characters()
                except ValueError as ve:
                    self.__error_logger.log(f"Error found:\n{ve}.")
                    print("Invalid character option.")
                except Exception as e:
                    self.__error_logger.log(f"Unexpected exception found for "
                                            f"player input to interact with "
                                            f"characters:\n{e}")
                    print("Unexpected error found for player input to "
                          "interact with character. We continue playing...")
            elif player_input.lower() == "e":
                self.examine_clues()
            elif player_input.lower() == "c":
                try:
                    self.choose_door()
                except ValueError as ve:
                    print("This carriage choice does not exist.")
                    self.__error_logger.log(f"Error found:\n{ve}")
                except Exception as e:
                    self.__error_logger.log(f"Unexpected error found for "
                                            f"player input:\n{e}")
                    print("Unexpected error from player input. We continue "
                          "playing...")
            elif player_input.lower() == "r":
                clues = self.__crime_scene.review_clues()
                if clues:
                    for clue in clues:
                        print("\033[94m" + clue + "\033[0m")
                else:
                    print("\033[93mYou have not found any clues yet.\033[0m")
            else:
                print("\033[91mIncorrect User gameoption choice made\033[0m")
                raise ValueError("Incorrect user game option choice made.")

    def start_game(self):
        self.__logger.log("Game is starting")

        pygame.mixer.music.load("intro.mp3")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(50)

        player_name = input("Enter your Agent's name: ")
        print(f"Welcome, Agent {player_name}!\n")

        self.play_background_sound()

        print("\033[38;2;64;224;208mYou find yourself on a luxurious train, en route to a UN summit in Vienna.")
        print(
            f"As the infamous interpol Agent {player_name}, you're here to solve the mysterious murder of the President of France.\n")
        print("The train is filled with world leaders, each with their own motives and secrets.")
        print("You have only 5 minutes to make an arrest before the train reaches Vienna.\n")
        print(
            "If the train reaches its destination before an arrest is made, the murderer will go free, sparking tensions between nations.")
        print("Your mission is to uncover the truth and prevent an international crisis.\033[0m\n")

    def interact_with_characters(self):
        self.player_stats.add_clue_found()  # Update clue count
        self.__logger.log("Interactions happening")
        print("\033[97mYou decide to interact with the characters outside the room.\033[0m")
        character = int(input(
            "\033[91mIf you want to speak to the people in the room, choose 1. \n\033[92mIf you'd like to speak to the people outside the room, choose 2: "))

        if character == 1:
            if not self.__characters_interacted:
                self.__logger.log("Interacting with suspects and witnesses.")
                print("\033[97mYou decide to interact with the characters in the room:\033[0m")

                clue_suspect = self.__suspect.interact()
                self.__crime_scene.add_clue(clue_suspect)
                print(clue_suspect)

                suspect_alibi = self.__suspect.provide_alibi()
                self.__crime_scene.add_clue(suspect_alibi)
                print(suspect_alibi)

                print(self.__suspect.perform_action())

                clue_witness = self.__witness.interact()
                self.__crime_scene.add_clue(clue_witness)
                print(clue_witness)

                witness_observation = self.__witness.share_observation()
                self.__crime_scene.add_clue(witness_observation)
                print(witness_observation)

                print(self.__witness.perform_action())

                self.__characters_interacted = True
            else:
                print(
                    "\033[93mYou have already interacted with the characters. They no longer wish to speak to you.\033[0m")
        elif character == 2:
            if not self.__npcs_interacted:
                self.__logger.log("Interacting with people outside the room.")
                print("\033[97mYou decide to speak to the characters outside and ask them for clues:\033[0m")
                indifferent_npc = NPC("Mr Germany",
                                      "\033[91mWelcome to my carriage,I will try to help as much as possible,france had terrible relations to almost every other nation so it could have been anyone\033[0m")
                friendly_npc = NPC("Ms Italy",
                                   "\033[32mPlease excuse the messy conditions of my carriage, I believe that it was either England or Spain as tensions has been rising for quite some time between france and the two nations.\033[0m")
                hostile_npc = NPC("Mr Spain",
                                  "\033[93mI can tell you the passcode for carriage two is 4545 ,But I will not speak to you on this matter!! what has happened to France has been a long time coming!!! Now Leave My Carriage\033[0m")

                characters = [indifferent_npc, friendly_npc, hostile_npc]

                for character in characters:
                    print(character.interact())
                    print(character.perform_action())

                self.__crime_scene.add_clue(
                    "Three people are hanging around the scene who have nothing to do with the crime.")
                self.__crime_scene.add_clue("Carriage 2 passcode : 4545")
                self.__npcs_interacted = True
            else:
                print("\033[93mPeople in the room are tired of you. They no longer want to speak to you.\033[0m")
        else:
            print("\033[91mThis is not an option for a character\033[0m")
            raise ValueError("This is not an option for a character.")

    def examine_clues(self):
        self.player_stats.add_clue_found()  # Update clue count
        self.__logger.log("Examination happening")
        print("\033[97mYou decide to examine the clues at the crime scene.\033[0m\n")
        if not self.__crime_scene.investigated:
            print(
                "You enter the room to find a nervous looking waiter, he tells you to check out carriage one and tells you the passcode before leaving the room.\n")
            print(
                "As you are walking out you see spot a tie pin with the Spanish flag embedded on it near the window,.\n")
            self.__crime_scene.add_clue("carriage 1 passcode : 6969")
            self.__crime_scene.add_clue("Spanish flag tie pin")
            self.__crime_scene.investigated = True
        else:
            print("You've already examined the crime scene clues.")

    def choose_door(self):
        self.__logger.log("Carriages are to be chosen")
        print("You decide to choose a Carriage to investigate:")

        for i, door in enumerate(self.__doors, start=1):
            print(f"{i}. {door}")

        door_choice = int(input("Enter the number of the Carriage you want to investigate: "))

        self.__logger.log(f"Player chooses to investigate door {door_choice}.")

        if 0 < door_choice < len(self.__doors) + 1:
            if door_choice == 1:
                if not self.__doors_checker[0]:
                    print("\033[97mYou approach the door to carriage 1\033[0m\n")
                    self.__logger.log("Carriage 1 has been investigated.")
                    self.give_password3()
                else:
                    print("You have looked in Carriage 1 already.\n")
                    self.__logger.log("Carriage 1 had been chosen before. No access.")
            elif door_choice == 2:
                if not self.__doors_checker[1]:
                    print("\033[97mYou approach the door to Carriage 2.\033[0m\n")
                    print("\033[97mThe door is locked and requires a passcode,")
                    self.__logger.log("Carriage 2 has been investigated.")
                    self.give_password2()
                else:
                    print("You've looked in Carriage 2 already.\n")
                    self.__logger.log("Carriage 2 had been chosen before. No access.")
            elif door_choice == 3:
                if not self.__doors_checker[2]:
                    print("You open the door to Carriage 3.")
                    print("\033[97mThere is a strange man asking for a password,")
                    print("he sounds as though he may be irish but hides his accent well.\033[0m")
                    self.__logger.log("Carriage 3 has been investigated.")
                    self.give_password()
                else:
                    print("You've looked in Carriage 3 already.")
                    self.__logger.log("Carriage 3 had been chosen before. No access.")
        else:
            print("\033[91mInvalid Carriage Choice\033[0m")
            raise ValueError(f"Invalid door choice: {door_choice}")

    def continue_game(self):
        print("You continue your investigation, determined to solve the mystery...")

        characters = [self.__suspect, self.__witness, NPC("Mr Germany", ""), NPC("Ms Italy", ""), NPC("Mr Spain", "")]

        print("\033[97mChoose a character you wish to arrest:\033[0m")
        print("\033[92mRemember you can only arrest one character SO CHOOSE WISELY!!!!\033[0m")
        for i, character in enumerate(characters, start=1):
            print(f"{i}. {character}")

        character_choice = int(input("\033[97mEnter the number of the character you want to arrest: \033[0m"))

        if 0 < character_choice <= len(characters):
            arrested_character = characters[character_choice - 1]

            self.player_stats.add_decision("Arrested " + arrested_character._name)  # Track decision

            # Display character-specific dialogue
            if arrested_character == self.__suspect:
                print(
                    f"{arrested_character._name}:\033[97m Im Not the only one who wanted him eliminated! France has been trying to provoke a war and disband the UN for years now, I was merely the only one out of us 5 nations willing to do what must be done.\033[0m")
            else:
                print(
                    f"{arrested_character._name}: \033[97m You got the wrong person! I had nothing to do with it.\033[0m")

            # Check if the correct character is arrested
            if arrested_character == self.__suspect:
                print(
                    "\033[92mCongratulations! You have made the correct arrest just as the train reaches its destination and prevented an international crisis.")
                print("The UN and the world thank you!\033[0m")  # Prints the output in green to make it more grahpically appealing  and to know immediatly if the user wins/loses

                additional_sound = pygame.mixer.Sound("Trumpets.mp3")
                additional_sound.play()

                # Wait for the additional sound to finish playing
                while pygame.mixer.get_busy():
                    pygame.time.Clock().tick(50)

                pygame.mixer.music.load("Victory.mp3")
                pygame.mixer.music.play()

                # Wait for the music to finish playing
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(50)

                self.__running = False  # End the game after making a correct arrest
            else:

                additional_sound = pygame.mixer.Sound("womp.mp3")
                additional_sound.play()

                # Wait for the additional sound to finish playing
                while pygame.mixer.get_busy():
                    pygame.time.Clock().tick(50)

                pygame.mixer.music.load("wrong.mp3")
                pygame.mixer.music.play()
                print("\033[91mYou have failed to make the correct arrest, and the real culprit has just disembarked the train.")
                print(
                    "This will lead to an international crisis.\033[0m")  # prints the losing output in red to stand out from the rest of the text so the user knows immediatly if they win or lose

                # Wait for the music to finish playing
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(20)  # Adjust the argument to control the wait time

                self.__running = False  # End the game after making an incorrect arrest
        else:
            print("\033[91mInvalid Character Choice\033[0m")
            raise ValueError(f"Invalid character choice for arrest: {character_choice}")

    def stop_background_sound(self):
        self.__running = False
        self.background_sound_thread.join()

    def give_password(self):
        self.__logger.log("Attempting to give password")
        password_attempt = input("Enter the password : ")
        if password_attempt.lower() == "oscail an doras":
            print("\033[97mCongratulations! The door opens.\033[0m")
            print("You find a blood-soaked knife with a harp emblem on it.")
            self.__crime_scene.add_clue("Blood-soaked Knife with Harp emblem")
            self.__doors_checker[2] = True
        else:
            print("Incorrect password. You return to the main menu.")

    def give_password2(self):
        password_attempt2 = input("Enter 4 digit passcode : ")
        if password_attempt2.lower() == "4545":
            print("Correct passcode, the door is open")
            print("You find an old man who whispers the phrase 'an doras' quietly")
            self.__crime_scene.add_clue("Phrase 'an doras'")
            self.__doors_checker[1] = True

        else:
            print("incorrect password. You return to the main menu.")

    def give_password3(self):
        passsword_attempt3 = input("Enter 4 digit passcode : ")
        if passsword_attempt3.lower() == "6969":
            print("Correct passcode, the door is open")
            print("You walk into the carriage to find a torn letter containing a single word.")
            self.__crime_scene.add_clue("Torn Letter Containing the word 'Oscail'")
            self.__doors_checker[0] = True
        else:
            print("incorrect password. You return to the main menu.")


if __name__ == "__main__":
    game = Game()
    game.title_screen()
    game.run()

    # Stop the background sound
    game.stop_background_sound()

    # Print game logs after a 5-second delay
    print("\nGame Logs: printing in 5 seconds")
    first_log = True
    for log in game.get_logs():
        if first_log:
            time.sleep(5)  # Add a 5-second delay
            first_log = False
        print(log)

    # Print game error logs
    print("\nGame Error Logs:")
    for log in game.get_error_logs():
        print(log)

    # Display player stats summary
    game.player_stats.display_summary()

