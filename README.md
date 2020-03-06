# Iron March message network visualization

This repository contains scripts, datasets, and intermediate files necessary for generating an interactive visualization of the Iron March messaging network, as well as the HTML file of the visualization itself.

Iron March was an influential neo-Nazi forum, which had its private user data leaked online recently.
For more information, see [this Bellingcat article][bellingcat]

The visualization was generated using the following steps:

0. Clean up the `core_message_topics.csv` file from the original leak: some rows had misaligned columns. I've included the edited file in the `csv/` directory. The rest of the CSV files are unchanged and can be downloaded using the links in the [Bellingcat article][bellingcat].

1. Extract node and edge information from the datasets provided by the leak, convert to a NetworkX graph, and export as a GEXF file. The file `scripts/generate_gexf.py` performs these actions.

2. Use the GEXF file to compute a graph layout using the open source [Gephi][gephi] graphing library, export a second GEXF file containing the computed locations of each node. I found that the most aesthetically pleasing results were obtained by:

    * using the *Force Atlas 2* layout algorithm
    * setting the node circle radius for a given user to be proportional to the base 10 logarithm of the number of posts made by the user
    * allowing the layout to equilibrate for a few minutes, before imposing the *Prevent Overlap* *Behavior Alternative*, and then waiting another few minutes for the layout to equilibrate.

3. Use the node locations from the second GEXF file to create a visualization using the [HoloViews][holoviews] package and the [Bokeh][bokeh] backend. The file `scripts/generate_visualization.py` performs these actions.

[bellingcat]: https://www.bellingcat.com/resources/how-tos/2019/11/06/massive-white-supremacist-message-board-leak-how-to-access-and-interpret-the-data/
[holoviews]: http://holoviews.org/
[bokeh]: https://docs.bokeh.org/en/latest/
[gephi]: https://gephi.org/