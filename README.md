# aumento-dados-ud

The code for our STIL23 paper "Proposta e Avaliação Linguística de Técnicas de Aumento de Dados". 

First you need to have a UD file to augment.
Then you can generate artificial data by running '**sh augment_single.sh**'. File parameters are:
- **infile**: UD file to augment
- **outfile**: Name of the output file
- **operation**: obl or advcl

The **obl** option moves an adverbial phrase, while the **advcl** option moves an adverbial clause. A txt file is also generated containing all the augmented sentences.