from datetime import datetime

class EVENT: 
    def __init__(self, event_name, time_values, user_id, time_string, remind_minutes = 15):
        self.name = event_name
        self.time_string = time_string
        self.time_value = None
        self.creator = user_id
        self.possible_times = time_values
        if(len(time_values) == 1): 
            self.select_timing(1)
        self.participants = [self.creator]
        self.remind_before = remind_minutes * 60
    
    def select_timing(self, value): 
        index = value - 1
        self.time_value = self.possible_times[index].replace(tzinfo = None)
        self.possible_times = None
        print("Set Time Value of " + str(self.name) + " to " + str(self.time_value))
    
    def check(self, current_time): 
        if(self.time_value is None): 
            return False
        difference = self.time_value - current_time
        if(difference.total_seconds() > self.remind_before): 
            return False
        return True
    
    def add_user(self, user_id): 
        if user_id not in self.participants: 
            self.participants.append(user_id)
            return True
        return False
    
    def remove_user(self, user_id): 
        if user_id in self.participants: 
            self.participants.remove(user_id)
            return True
        return False
    
    def is_participant(self, user_id): 
        return user_id in self.participants