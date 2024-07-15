class Recorder(list):
    def __init__(self):
      self.clear() 

    def clear(self):
        super().clear()
        self.indent = 0
        self.repeat = 0
        self.rcount = []
        self.open_close = 0

    def in_repeat(self):
        self.repeat += 1
        self.rcount.append(1)
    
    def out_repeat(self):
        self.repeat -= 1
        self.rcount.pop()
        
        # At the end of "repeat",
        # previous "repeat" should be increased
        if self.rcount:
            self.rcount[-1] += 1


    def is_first_step_in_repeat(self):
        return self.repeat > 0 and self.open_close == 0 

thread_recorder = {}
recorder = Recorder()

def record(rec: Recorder, formatter: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            x = kwargs.get("tid", -1)

            if isinstance(args[-1], int):
                x = args[-1]

            reca = rec
            if x != -1:
                reca = thread_recorder[x]
            obj = args[0]
            #repeat object behavior
            if obj.name == "Repeat":
                reca.in_repeat()
                result = func(*args, **kwargs) 
                reca.append(formatter.format(**obj.outcome) + "\n")
                reca.out_repeat()
                return result

            #other object behavior
            if reca.is_first_step_in_repeat():
                count = "-".join(map(str, reca.rcount))
                reca.append(f"#{count}")
                reca.rcount[rec.repeat-1] += 1
            
            if reca.repeat > 0:
                reca.open_close += 1

            result = func(*args, **kwargs)

            if obj.name != "Repeat" and reca.repeat > 0:
                reca.open_close -= 1

            reca.append(formatter.format(**obj.outcome))
            if reca.repeat > 0 and reca.open_close == 0:
                reca.append(" ")

            return result
        return wrapper
    return decorator
