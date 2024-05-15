## TrajVis: Balloon Trajectory Visualization Tool

TrajVis is a Python-based tool to visualize the trajectories of stratospheric (or high-altitude) balloon flights based on a randomly generated windy environment.

The features of this tool

- Simulating an adhoc environment for a single or multiple balloon(s)
- Calculating mesh networks using multiple balloons
- Providing a "testbed" tool that can be extended to simulate stratospheric-based research questions.

### Setup and Usage

Install the requirements that are found in `requirements.txt`:

```
pip install -r requirements.txt
```

This tool is provided as a set of "components" (classes) that can be used within your own code. An example simulation is provided in `sim.ipynb`, and a code verification file is provided as `verify.py`.

### Documentation

As mentioned, the tool is provided as a set of classes. Documentation for each of the classes is provided in the [/docs](/docs/) folder in this repository.

### Authors

- Ali Mosallaei, [alimos@umich.edu](mailto:alimos@umich.edu)
- Daniil Voloshin, [daniilv@umich.edu](mailto:daniilv@umich.edu)
- Dr. James W. Cutler, [jwcutler@umich.edu](mailto:jwcutler@umich.edu)

*TrajVis was developed at the Michigan eXploration Lab, a research lab at the University of Michigan in Ann Arbor, MI. TrajVis was developed with funding in part provided by NASA JPL's Strategic University Research Partnerships (SURP) program.*
