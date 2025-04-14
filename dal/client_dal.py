from sqlalchemy.orm import Session
from models.client import Client
from dtos.client_dto import ClientDTO


class ClientDAL:
    def __init__(self, db: Session):
        self.db = db

    def _to_dto(self, client: Client) -> ClientDTO:
        """
        Converts a `Client` object to a `ClientDTO` object.

        The method maps all relevant fields from a `Client` entity to its
        corresponding data transfer object (`ClientDTO`), which can be utilized
        in data transactions across different layers or components.

        :param client: The `Client` object to be converted.
        :type client: Client
        :return: A data transfer object (`ClientDTO`) representing the input
            `Client` entity with its attributes mapped accordingly.
        :rtype: ClientDTO
        """
        return ClientDTO(
            id=client.id,
            name=client.name,
            email=client.email,
            phone=client.phone,
            company=client.company,
            creation_date=client.creation_date,
            last_contact_date=client.last_contact_date,
            commercial_id=client.commercial_id,
        )

    def get(self, client_id: int) -> ClientDTO | None:
        """
        Fetches a client record from the database by its identifier and converts it into
        a Data Transfer Object (DTO). Returns None if no matching client is found.

        :param client_id: The unique identifier of the client to retrieve.
        :type client_id: int
        :return: A ClientDTO object representing the client record if found, otherwise None.
        :rtype: ClientDTO | None
        """
        client = self.db.query(Client).filter_by(id=client_id).first()
        if not client:
            return None
        return self._to_dto(client)

    def create(self, data: dict) -> ClientDTO:
        """
        Creates a new client record in the database and returns its Data Transfer Object (DTO)
        representation.

        This method instantiates a Client object from the provided data dictionary, adds the
        client record to the database, commits the transaction, refreshes the state, and
        converts it to a DTO before returning it.

        :param data: Dictionary containing client data to be stored in the database.
        :type data: dict
        :return: A Data Transfer Object (DTO) representing the created client record.
        :rtype: ClientDTO
        """
        client = Client(**data)
        self.db.add(client)
        self.db.commit()
        self.db.refresh(client)
        return self._to_dto(client)

    def get_by_email(self, email: str) -> ClientDTO | None:
        client = self.db.query(Client).filter_by(email=email).first()
        return self._to_dto(client) if client else None

    def update(self, client: Client, updates: dict) -> ClientDTO:
        for key, value in updates.items():
            setattr(client, key, value)
        self.db.commit()
        self.db.refresh(client)
        return self._to_dto(client)

    def update_by_id(self, client_id: int, updates: dict) -> ClientDTO:
        client = self.db.query(Client).filter_by(id=client_id).first()
        if not client:
            return None
        return self.update(client, updates)

    def get_raw(self, client_id: int) -> Client | None:
        """
        Retrieve raw client data by client ID.

        This method is used to fetch the client information using the client ID. If the
        client ID is found, the corresponding client data is returned. If not, the
        method returns None.

        :param client_id: Unique identifier for the client.
        :type client_id: int
        :return: The client object if found, otherwise None.
        :rtype: Client | None
        """
        return self.db.query(Client).filter_by(id=client_id).first()