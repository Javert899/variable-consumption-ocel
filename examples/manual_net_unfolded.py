import pm4py
from pm4py.objects.petri_net.obj import PetriNet, Marking
from pm4py.objects.petri_net.utils import petri_utils
from uuid import uuid4


neto = PetriNet()
imo = Marking()
fmo = Marking()
sourceo = PetriNet.Place("sourceo")
targeto = PetriNet.Place("targeto")
imo[sourceo] = 1
fmo[targeto] = 1
neto.places.add(sourceo)
neto.places.add(targeto)
create_order_o = PetriNet.Transition(str(uuid4()), "Create Order")
send_package_o = PetriNet.Transition(str(uuid4()), "Send Package")
pay_order_o = PetriNet.Transition(str(uuid4()), "Pay Order")
item_issue_o = PetriNet.Transition(str(uuid4()), "Item Issue")
item_fixed_o = PetriNet.Transition(str(uuid4()), "Item Fixed")
skip_o = PetriNet.Transition(str(uuid4()), None)
neto.transitions.add(create_order_o)
neto.transitions.add(send_package_o)
neto.transitions.add(pay_order_o)
neto.transitions.add(item_issue_o)
neto.transitions.add(item_fixed_o)
neto.transitions.add(skip_o)
p1o = PetriNet.Place("p1o")
p2o = PetriNet.Place("p2o")
p3o = PetriNet.Place("p3o")
p4o = PetriNet.Place("p4o")
neto.places.add(p1o)
neto.places.add(p2o)
neto.places.add(p3o)
neto.places.add(p4o)
arc1o = petri_utils.add_arc_from_to(sourceo, create_order_o, neto)
arc2o = petri_utils.add_arc_from_to(create_order_o, p1o, neto)
arc3o = petri_utils.add_arc_from_to(p1o, item_issue_o, neto)
arc4o = petri_utils.add_arc_from_to(p1o, skip_o, neto)
arc5o = petri_utils.add_arc_from_to(item_issue_o, p2o, neto)
arc6o = petri_utils.add_arc_from_to(p2o, item_fixed_o, neto)
arc7o = petri_utils.add_arc_from_to(item_fixed_o, p3o, neto)
arc8o = petri_utils.add_arc_from_to(p3o, send_package_o, neto)
arc9o = petri_utils.add_arc_from_to(skip_o, p3o, neto)
arc10o = petri_utils.add_arc_from_to(send_package_o, p4o, neto)
arc11o = petri_utils.add_arc_from_to(p4o, pay_order_o, neto)
arc12o = petri_utils.add_arc_from_to(pay_order_o, targeto, neto)
arc1o.histogram = {1: 1.0}
arc2o.histogram = {1: 1.0}
arc3o.histogram = {1: 1.0}
arc4o.histogram = {1: 1.0}
arc5o.histogram = {1: 1.0}
arc6o.histogram = {1: 1.0}
arc7o.histogram = {1: 1.0}
arc8o.histogram = {1: 1.0}
arc9o.histogram = {1: 1.0}
arc10o.histogram = {1: 1.0}

#pm4py.view_petri_net(neto, imo, fmo, format="svg")

neti = PetriNet()
imi = Marking()
fmi = Marking()
sourcei = PetriNet.Place("sourcei")
targeti = PetriNet.Place("targeti")
imi[sourcei] = 3
fmi[targeti] = 3
neti.places.add(sourcei)
neti.places.add(targeti)
create_order_i2 = PetriNet.Transition(str(uuid4()), "Create Order")
send_package_i2 = PetriNet.Transition(str(uuid4()), "Send Package")
item_issue_i1 = PetriNet.Transition(str(uuid4()), "Item Issue")
item_fixed_i1 = PetriNet.Transition(str(uuid4()), "Item Fixed")
create_order_i3 = PetriNet.Transition(str(uuid4()), "Create Order")
send_package_i3 = PetriNet.Transition(str(uuid4()), "Send Package")
skip_i2 = PetriNet.Transition(str(uuid4()), None)
skip_i3 = PetriNet.Transition(str(uuid4()), None)
neti.transitions.add(create_order_i2)
neti.transitions.add(send_package_i2)
neti.transitions.add(item_issue_i1)
neti.transitions.add(item_fixed_i1)
neti.transitions.add(create_order_i3)
neti.transitions.add(send_package_i3)
neti.transitions.add(skip_i2)
neti.transitions.add(skip_i3)
p1i = PetriNet.Place("p1i")
p2i = PetriNet.Place("p2i")
p3i = PetriNet.Place("p3i")
neti.places.add(p1i)
neti.places.add(p2i)
neti.places.add(p3i)
petri_utils.add_arc_from_to(sourcei, create_order_i2, neti, weight=2)
petri_utils.add_arc_from_to(create_order_i2, p1i, neti, weight=2)
petri_utils.add_arc_from_to(sourcei, create_order_i3, neti, weight=3)
petri_utils.add_arc_from_to(create_order_i3, p1i, neti, weight=3)
petri_utils.add_arc_from_to(p1i, item_issue_i1, neti, weight=1)
petri_utils.add_arc_from_to(p1i, skip_i2, neti, weight=2)
petri_utils.add_arc_from_to(p1i, skip_i3, neti, weight=3)
petri_utils.add_arc_from_to(item_issue_i1, p2i, neti, weight=1)
petri_utils.add_arc_from_to(p2i, item_fixed_i1, neti, weight=1)
petri_utils.add_arc_from_to(p3i, send_package_i2, neti, weight=2)
petri_utils.add_arc_from_to(p3i, send_package_i3, neti, weight=3)
petri_utils.add_arc_from_to(skip_i2, p3i, neti, weight=2)
petri_utils.add_arc_from_to(skip_i3, p3i, neti, weight=3)
petri_utils.add_arc_from_to(item_fixed_i1, p3i, neti, weight=1)
petri_utils.add_arc_from_to(send_package_i2, targeti, neti, weight=2)
petri_utils.add_arc_from_to(send_package_i3, targeti, neti, weight=3)

#pm4py.view_petri_net(neti, imi, fmi, format="svg")

nete = PetriNet()
ime = Marking()
fme = Marking()
sourcee = PetriNet.Place("source")
targete = PetriNet.Place("targete")
nete.places.add(sourcee)
nete.places.add(targete)
ime[sourcee] = 1
fme[targete] = 1
create_order_e = PetriNet.Transition(str(uuid4()), "Create Order")
send_package_e = PetriNet.Transition(str(uuid4()), "Send Package")
item_issue_e = PetriNet.Transition(str(uuid4()), "Item Issue")
item_fixed_e = PetriNet.Transition(str(uuid4()), "Item Fixed")
skip_e = PetriNet.Transition(str(uuid4()), None)
nete.transitions.add(create_order_e)
nete.transitions.add(send_package_e)
nete.transitions.add(item_issue_e)
nete.transitions.add(item_fixed_e)
nete.transitions.add(skip_e)
p1e = PetriNet.Place("p1e")
p2e = PetriNet.Place("p2e")
p3e = PetriNet.Place("p3e")
nete.places.add(p1e)
nete.places.add(p2e)
nete.places.add(p3e)
arc1 = petri_utils.add_arc_from_to(sourcee, create_order_e, nete)
arc2 = petri_utils.add_arc_from_to(create_order_e, p1e, nete)
arc3 = petri_utils.add_arc_from_to(p1e, skip_e, nete)
arc4 = petri_utils.add_arc_from_to(p1e, item_issue_e, nete)
arc5 = petri_utils.add_arc_from_to(item_issue_e, p2e, nete)
arc6 = petri_utils.add_arc_from_to(p2e, item_fixed_e, nete)
arc7 = petri_utils.add_arc_from_to(item_fixed_e, p3e, nete)
arc8 = petri_utils.add_arc_from_to(skip_e, p3e, nete)
arc9 = petri_utils.add_arc_from_to(p3e, send_package_e, nete)
arc10 = petri_utils.add_arc_from_to(send_package_e, targete, nete)
arc1.histogram = {2: 0.5, 3: 0.5}
arc2.histogram = {2: 0.5, 3: 0.5}
arc3.histogram = {2: 0.666667, 3: 0.333333}
arc4.histogram = {1: 1}
arc5.histogram = {1: 1}
arc6.histogram = {1: 1}
arc7.histogram = {1: 1}
arc8.histogram = {2: 0.666667, 3: 0.333333}
arc9.histogram = {2: 0.5, 3: 0.5}
arc10.histogram = {2: 0.5, 3: 0.5}

arc1.weight = str(arc1.histogram)
arc2.weight = str(arc2.histogram)
arc3.weight = str(arc3.histogram)
arc4.weight = str(arc4.histogram)
arc5.weight = str(arc5.histogram)
arc6.weight = str(arc6.histogram)
arc7.weight = str(arc7.histogram)
arc8.weight = str(arc8.histogram)
arc9.weight = str(arc9.histogram)
arc10.weight = str(arc10.histogram)

pm4py.view_petri_net(nete, ime, fme, format="svg")
