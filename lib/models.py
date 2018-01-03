from subconscious.model import RedisModel
from subconscious.column import Column

class Transactions(RedisModel):

    uuid = Column(type=str, primary_key=True)
    tx_index = Column(type=int, required=True)
    addr = Column(index=True, type=str, sort=True, required=True)
    value = Column(type=int, index=True)