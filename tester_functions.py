from application.application import Application
from application.encoder import Encoder

def test_application():
    app_delay = Application(
        name = "application delay", traffic_type="Exponential", length=32,
        params={"lambda": 1}
    )
    print(app_delay.get_traffic_delay())
    
def test_encoder():
    encoder_delay = Encoder(
        name = "application delay", traffic_type="Exponential", length=32,
        params={"lambda": 2}
    )
    print(encoder_delay.get_traffic_delay())
