from io import TextIOWrapper

class T3DFile(object):
    def __init__(self) -> None:
        self.commands = []
    
    def add_command(self, name):
        command = T3DCommand(name)
        self.commands.append(command)
        return command
    
class T3DCommand(object):
    def __init__(self, name):
        self.name = name
        self.data = []
        self.children = []
        self.sub_commands = []

    @property
    def has_data(self):
        return len(self.data) > 0

    @property
    def has_children(self):
        return len(self.children)

    @property
    def has_sub_commands(self):
        return len(self.sub_commands) > 0

    def push_datum(self, datum):
        self.data.append(datum)
        return self

    def push_data(self, data):
        self.data += data
        return self

    def push_sub_command(self, name):
        command = T3DCommand(name)
        self.sub_commands.append(command)
        return command

    def push_child(self, name):
        child = T3DCommand(name)
        self.children.append(child)
        return child

class T3DWriter:
    def __init__(self):
        self.fp : TextIOWrapper
        self.indent = 0

    def write_datum(self, datum):
        if type(datum) is str:
            self.fp.write(datum)
        elif type(datum) is int:
            self.fp.write(str(datum))
        elif type(datum) is float:
            self.fp.write('{:0.4f}'.format(datum))
        elif type(datum) is dict:
            for index, (key, value) in enumerate(datum.items()):
                if index > 0:
                    self.fp.write(' ')
                self.fp.write(f'{key}: ')
                self.write_datum(value)

    def write_sub_command(self, sub_command):
        self.fp.write(f' *{sub_command.name}')
        if sub_command.has_data:
            for datum in sub_command.data:
                self.fp.write(' ')
                self.write_datum(datum)

    def write_command(self, command):
        self.fp.write('\t' * self.indent)
        self.fp.write(f'*{command.name}')
        if command.has_data:
            for datum in command.data:
                self.fp.write(' ')
                self.write_datum(datum)
        if command.has_sub_commands:
            # Sub-commands are commands that appear inline with their parent command
            for sub_command in command.sub_commands:
                self.write_sub_command(sub_command)
        if command.has_children:
            self.fp.write(' {\n')
            self.indent += 1
            for child in command.children:
                self.write_command(child)
            self.indent -= 1
            self.fp.write('\t' * self.indent + '}\n')
        else:
            self.fp.write('\n')

    def write_file(self, file : T3DFile):
        for command in file.commands:
            self.write_command(command)

    def begin(file : T3DFile):
        file += \
        "Begin Map\n \
            Begin Level NAME=PersistentLevel\n \
                Begin Actor Class=WorldInfo Name=WorldInfo_0 Archetype=WorldInfo'Engine.Default__WorldInfo'\n \
                bMapNeedsLightingFullyRebuilt=True\n \
                bPathsRebuilt=True\n \
                DefaultPostProcessSettings=(Curves=(Ms[0]=(X=1.000000,Y=1.000000,Z=1.000000),Ms[1]=(X=1.000000,Y=1.000000,Z=1.000000),Ms[2]=(X=1.000000,Y=1.000000,Z=1.000000),Ms[3]=(X=1.000000,Y=1.000000,Z=1.000000),Ms[4]=(X=1.000000,Y=1.000000,Z=1.000000),Ms[5]=(X=1.000000,Y=1.000000,Z=1.000000),Ms[6]=(X=1.000000,Y=1.000000,Z=1.000000),Ms[7]=(X=1.000000,Y=1.000000,Z=1.000000),Ms[8]=(X=1.000000,Y=1.000000,Z=1.000000),Ms[9]=(X=1.000000,Y=1.000000,Z=1.000000),Ms[10]=(X=1.000000,Y=1.000000,Z=1.000000),Ms[11]=(X=1.000000,Y=1.000000,Z=1.000000),Ms[12]=(X=1.000000,Y=1.000000,Z=1.000000),Ms[13]=(X=1.000000,Y=1.000000,Z=1.000000),Ms[14]=(X=1.000000,Y=1.000000,Z=1.000000),Ms[15]=(X=1.000000,Y=1.000000,Z=1.000000)))\n \
                TimeSeconds=15147.450195\n \
                RealTimeSeconds=17638.800781\n \
                AudioTimeSeconds=17638.800781\n \
                Tag=\"WorldInfo\" \
                Name=\"WorldInfo_0\" \
                ObjectArchetype=WorldInfo'Engine.Default__WorldInfo'\n \
            End Actor\n"
        
    def end(file : T3DFile):
        file += \
            "End Level\n \
        Begin Surface\n \
        End Surface\n \
        End Map\n"
    
    def write(self, filepath, t3d):
        self.indent = 0
        t3d_file = self.build_t3d_tree(t3d)
        with open(filepath, 'w') as self.fp:
            self.write_file(t3d_file); 
