
# Stark Bank Project

Consuming StarkBank API do made Payments if some invoice is created for our account.


### Start

#### Docker build
`docker  build -t stark_container `

#### Docker Start

`docker run --name sb_container -p 8080:8080 --network net stark_container`


### Run Tests

`docker run --rm stark_container pytest`

