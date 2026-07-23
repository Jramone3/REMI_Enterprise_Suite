// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PrediccionMercado {
    address payable public owner;
    uint256 public precioConsulta = 0.01 ether;

    event ConsultaPagada(address indexed cliente, uint256 monto, uint256 timestamp);
    event PrecioActualizado(uint256 nuevoPrecio);

    modifier onlyOwner() {
        require(msg.sender == owner, "No eres el Custodio");
        _;
    }

    constructor() {
        owner = payable(msg.sender);
    }

    function setPrecio(uint256 _nuevoPrecio) public onlyOwner {
        precioConsulta = _nuevoPrecio;
        emit PrecioActualizado(_nuevoPrecio);
    }

    function pagarConsulta() public payable {
        require(msg.value >= precioConsulta, "Saldo insuficiente");
        emit ConsultaPagada(msg.sender, msg.value, block.timestamp);
    }

    receive() external payable {
        pagarConsulta();
    }

    function retirarFondos() public onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No hay fondos");
        (bool success, ) = owner.call{value: balance}("");
        require(success, "Fallo en la transferencia");
    }
}
