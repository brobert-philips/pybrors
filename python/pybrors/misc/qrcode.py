# File: misc/qrcode.py

# Import packages and submodules
import qrcode
import qrcode.image.svg

# Import classes and methods


class QRcode:

    def __init__(self) -> None:
        """
        Initialize the object.

        This function is the constructor of the class. It initializes
        the object and sets up the QRCode generator with the specified
        parameters.
        """
        self.qrcode = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )

    def create_contact(self) -> None:
        """
        Create a contact in the QR code.

        This function fills the vcard with the contact information,
        including the person's name, organization, title, email, and
        telephone number.
        """
        # Fill vcard
        self.qrcode.add_data("BEGIN:VCARD\r\nVERSION:3.0\r\n")
        self.qrcode.add_data("N:Robert;Benjamin\r\n")
        self.qrcode.add_data("ORG:United Imaging Healthcare;\r\n")
        self.qrcode.add_data("TITLE:Lead MRI Research Collaboration Scientist\r\n")
        self.qrcode.add_data("EMAIL:benjamin.robert@united-imaging.com\r\n")
        self.qrcode.add_data("TEL:+33 6 51 06 75 27\r\n")
        self.qrcode.add_data("END:VCARD\r\n")

    def save_png(self, file_path: str = None, color: str = "#000000") -> None:
        """
        Save a PNG image of the generated QR code.

        Parameters
        ----------
        file_path : str
            The file path to save the PNG image. If not provided, the
            image will not be saved. Defaults to None.
        color : str
            The color of the QR code. Defaults to "#000000".
        """
        # Generate qrcode
        self.qrcode.make(fit=True)
        img = self.qrcode.make_image(fill_color=color, back_color="white")

        # Save qrcode
        img.save(file_path)
