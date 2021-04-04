# MongoDB Exercises

## Installation

for python

```bash
$ python -m pip install pymongo
```

in local terminal

```bash
$ docker-compose down -v
$ docker-compose up -d
```

## Usage

```bash
$ docker exec -it mongodb mongo "localhost/pantip" -u root -p password --authenticationDatabase admin
```

## Webpage

- [ranking](http://localhost/rank) - ranking board

- [localhost](http://localhost/) - home page

  - click `Start` to start the game (insert a record to collection `game`)
  - click `Ranking` to view the top 5 records (rank by score)

- after click `Start`

  - you can typing or click `A, B, C, or D` button
  - you can't send your guess, when it's lenght < 4
  - you can press 'delete' to remove last alphabet
  - you can press enter or click `Submit` to check your guess (update last record)
  - you can show/hide your hint using url param name `hint`

- after your guess is correct

  - click `Play Again` to play another question (another random alphabets)

## Contact

- Nanthakarn Limkool - student ID: 6210545505
  - nanthakarn18@gmail.com
  - https://github.com/ZEZAY
