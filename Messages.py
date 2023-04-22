class Messages():
	TYPES = {
			'MASTER': 0,
			'REQUEST': 1,
			'ORDER': 2
		}
	def __init__(self, sender, receiver):
		self.sender = sender;
		self.receiver = receiver;

	def __str__(self) -> str:
		output = ''
		if self.sender:
			output += 'Sender : ' + str(self.sender.id)
		if self.receiver:
			output += ', Receiver : ' + str(self.receiver.id)
		return output


class Master(Messages):
	def __init__(self, sender, receiver):
		super().__init__(sender, receiver);
		self.type = Messages.TYPES['MASTER']

	def __str__(self) -> str:
		return super().__str__() + 'Master'

class Request(Messages):
	def __init__(self, sender, receiver, directions: list, isPushing: bool, isPulling: bool):
		super().__init__(sender, receiver);
		self.type = Messages.TYPES['REQUEST'];
		self.directions = directions;
		self.isPushing = isPushing;
		self.isPulling = isPulling;

	def __str__(self) -> str:
		return super().__str__() + 'Request'

class Order(Messages):
	def __init__(self, sender, receiver, direction: tuple):
		super().__init__(sender, receiver);
		self.type = Messages.TYPES['ORDER'];
		self.direction = direction;

	def __str__(self) -> str:
		return super().__str__() + ', Direction : ' + str(self.direction) + 'Order'