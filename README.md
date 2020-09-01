# LoL recommendation system

LoL recommendation system is a Python program which helps League of Legends (LoL) players make better champion picks and improve their intuition of synergies and counters of champions. System uses basic logistic regression model learnt on about 35k unique LoL matches from top leagues in 5 regions (Europe West, Europe Nordic East, Korea, Brasil, North America). Feature creation is based on these used in papers about prediction and recommendation systems in DoTA. [[1](http://cs229.stanford.edu/proj2013/PerryConley-HowDoesHeSawMeARecommendationEngineForPickingHeroesInDota2.pdf)][[2](https://pdfs.semanticscholar.org/7745/27ade8b86447c788a0d2b1618712c400e340.pdf)][[3](http://jmcauley.ucsd.edu/cse258/projects/fa15/018.pdf)]

## Installation
To install simply clone github repository with:
```
git clone https://github.com/franul/lol_recommendation_system.git
```
To run program got to repository location, install required packages with:
```
pip install -r requirements.txt
```
and run program with:
```
streamlit run run_streamlit.py
```

System on streamlit site should look like this:
<p align="center">
  <img src="http://g.recordit.co/IjfpxcA59s.gif"]>
</p>

Another way you could run this program is to edit bans and picks via textfiles in data directory and then run python script:
```
python run.py data/bans.txt data/champions.txt data
```
Recommendations.txt should contain your output.


