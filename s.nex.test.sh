# ---
echo "testing with gpt model_api and nex robot"
export DEATH=20
sh s.nuke.sh
python3 o.body.py --model_api gpt --robot nex &
python3 o.look.py --model_api gpt &
python3 o.plan.py --model_api gpt &
python3 o.talk.py --model_api gpt
# ---
echo "testing with rep model_api and nex robot"
export DEATH=20
sh s.nuke.sh
python3 o.body.py --model_api rep --robot nex &
python3 o.look.py --model_api rep &
python3 o.plan.py --model_api rep &
python3 o.talk.py --model_api rep