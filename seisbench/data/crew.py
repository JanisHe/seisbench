import seisbench.util
from seisbench.data.base import BenchmarkDataset


class CREW(BenchmarkDataset):
    """
    Curated Regional Earthquake Waveforms (CREW dataset)

    """

    def __init__(self, component_order="ENZ", **kwargs):
        citation = (
        "Aguilar Suarez, A. L., & Beroza, G. (2024). "
        "Curated Regional Earthquake Waveforms (CREW) Dataset. "
        "Seismica, 3(1). https://doi.org/10.26443/seismica.v3i1.1049"
        )

        self._write_chunk_file()

        super().__init__(
            citation=citation,
            repository_lookup=True,
            component_order=component_order,
            **kwargs,
        )

    @staticmethod
    def available_chunks(*args, **kwargs):
        return [
            "000",
            "001",
            "002",
            "003",
            "004",
            "005",
            "006",
            "007",
            "008",
            "009",
            "010",
            "011",
            "012",
            "013",
            "014",
            "015",
            "016",
            "017",
            "018",
            "019",
            "020",
            "021",
            "022",
            "023",
            "024",
            "025",
            "026",
            "027",
            "028",
            "029",
            "030",
            "031",
            "032",
            "033",
            "034",
            "035",
            "036",
            "037",
            "038",
            "039",
            "040",
            "041",
            "042",
            "043",
            "044",
            "045",
            "046",
            "047",
            "048",
            "049",
            "050",
            "052",
            "053",
            "054",
            "055",
            "056",
            "057",
            "058",
            "059",
            "060",
            "061",
            "062",
            "063",
            "064",
            "065",
            "066",
            "067",
            "068",
            "069",
            "070",
            "071",
            "072",
            "073",
            "074",
            "075",
            "076",
            "077",
            "078",
            "079",
            "080",
            "081",
            "082",
            "083",
            "084",
            "085",
            "086",
            "087",
            "088",
            "089",
            "090",
            "091",
            "092",
            "093",
            "094",
            "095",
            "096",
            "097",
            "098",
            "099",
            "100",
            "101",
            "102",
            "103",
            "104",
            "105",
            "106",
            "107",
            "108",
            "109",
            "110",
            "111",
            "112",
            "113",
            "114",
            "115",
            "116",
            "117",
            "118",
            "119",
            "120",
            "121",
            "122",
            "123",
            "124",
            "125",
            "126",
            "127",
            "128",
            "129",
            "130",
            "131",
            "132",
            "133",
            "134",
            "135",
            "136",
            "137",
            "138",
            "139",
            "140",
            "141",
            "142",
            "143",
            "144",
            "145",
            "146",
            "147",
            "148",
            "149",
            "150",
            "151",
            "152",
            "153",
            "154",
            "155",
            "156",
        ]

    def _write_chunk_file(self):
        """
        Write out the chunk file

        :return: None
        """
        chunks_path = self.path / "chunks"

        if chunks_path.is_file():
            return

        chunks = self.available_chunks()
        chunks_str = "\n".join(chunks) + "\n"

        self.path.mkdir(exist_ok=True, parents=True)
        with open(chunks_path, "w") as f:
            f.write(chunks_str)

    def _download_dataset(self, writer, chunk, **kwargs):
        path = self.path
        path.mkdir(parents=True, exist_ok=True)

        files = {
            "chunks": "https://nextcloud.gfz-potsdam.de/s/m2HxZc73eY6B7q9",
            "metadata000.csv":
            "metadata001.csv":
            "metadata002.csv":
            "metadata003.csv":
            "metadata004.csv":
            "metadata005.csv":
            "metadata006.csv":
            "metadata007.csv":
            "metadata008.csv":
            "metadata009.csv":
            "metadata010.csv":
            "metadata011.csv":
            "metadata012.csv":
            "metadata013.csv":
            "metadata014.csv":
            "metadata015.csv":
            "metadata016.csv":
            "metadata017.csv":
            "metadata018.csv":
            "metadata019.csv":
            "metadata020.csv":
            "metadata021.csv":
            "metadata022.csv":
            "metadata023.csv":
            "metadata024.csv":
            "metadata025.csv":
            "metadata026.csv":
            "metadata027.csv":
            "metadata028.csv":
            "metadata029.csv":
            "metadata030.csv":
            "metadata031.csv":
            "metadata032.csv":
            "metadata033.csv":
            "metadata034.csv":
            "metadata035.csv":
            "metadata036.csv":
            "metadata037.csv":
            "metadata038.csv":
            "metadata039.csv":
            "metadata040.csv":
            "metadata041.csv":
            "metadata042.csv":
            "metadata043.csv":
            "metadata044.csv":
            "metadata045.csv":
            "metadata046.csv":
            "metadata047.csv":
            "metadata048.csv":
            "metadata049.csv":
            "metadata050.csv":
            "metadata052.csv":
            "metadata053.csv":
            "metadata054.csv":
            "metadata055.csv":
            "metadata056.csv":
            "metadata057.csv":
            "metadata058.csv":
            "metadata059.csv":
            "metadata060.csv":
            "metadata061.csv":
            "metadata062.csv":
            "metadata063.csv":
            "metadata064.csv":
            "metadata065.csv":
            "metadata066.csv":
            "metadata067.csv":
            "metadata068.csv":
            "metadata069.csv":
            "metadata070.csv":
            "metadata071.csv":
            "metadata072.csv":
            "metadata073.csv":
            "metadata074.csv":
            "metadata075.csv":
            "metadata076.csv":
            "metadata077.csv":
            "metadata078.csv":
            "metadata079.csv":
            "metadata080.csv":
            "metadata081.csv":
            "metadata082.csv":
            "metadata083.csv":
            "metadata084.csv":
            "metadata085.csv":
            "metadata086.csv":
            "metadata087.csv":
            "metadata088.csv":
            "metadata089.csv":
            "metadata090.csv":
            "metadata091.csv":
            "metadata092.csv":
            "metadata093.csv":
            "metadata094.csv":
            "metadata095.csv":
            "metadata096.csv":
            "metadata097.csv":
            "metadata098.csv":
            "metadata099.csv":
            "metadata100.csv":
            "metadata101.csv":
            "metadata102.csv":
            "metadata103.csv":
            "metadata104.csv":
            "metadata105.csv":
            "metadata106.csv":
            "metadata107.csv":
            "metadata108.csv":
            "metadata109.csv":
            "metadata110.csv":
            "metadata111.csv":
            "metadata112.csv":
            "metadata113.csv":
            "metadata114.csv":
            "metadata115.csv":
            "metadata116.csv":
            "metadata117.csv":
            "metadata118.csv":
            "metadata119.csv":
            "metadata120.csv":
            "metadata121.csv":
            "metadata122.csv":
            "metadata123.csv":
            "metadata124.csv":
            "metadata125.csv":
            "metadata126.csv":
            "metadata127.csv":
            "metadata128.csv":
            "metadata129.csv":
            "metadata130.csv":
            "metadata131.csv":
            "metadata132.csv":
            "metadata133.csv":
            "metadata134.csv":
            "metadata135.csv":
            "metadata136.csv":
            "metadata137.csv":
            "metadata138.csv":
            "metadata139.csv":
            "metadata140.csv":
            "metadata141.csv":
            "metadata142.csv":
            "metadata143.csv":
            "metadata144.csv":
            "metadata145.csv":
            "metadata146.csv":
            "metadata147.csv":
            "metadata148.csv":
            "metadata149.csv":
            "metadata150.csv":
            "metadata151.csv":
            "metadata152.csv":
            "metadata153.csv":
            "metadata154.csv":
            "metadata155.csv":
            "metadata156.csv": 
            "waveforms001.hdf5":
            "waveforms002.hdf5":
            "waveforms003.hdf5":
            "waveforms004.hdf5":
            "waveforms005.hdf5":
            "waveforms006.hdf5":
            "waveforms007.hdf5":
            "waveforms008.hdf5":
            "waveforms009.hdf5":
            "waveforms010.hdf5":
            "waveforms000.hdf5":
            "waveforms001.hdf5":
            "waveforms002.hdf5":
            "waveforms003.hdf5":
            "waveforms004.hdf5":
            "waveforms005.hdf5":
            "waveforms006.hdf5":
            "waveforms007.hdf5":
            "waveforms008.hdf5":
            "waveforms009.hdf5":
            "waveforms010.hdf5":
            "waveforms011.hdf5":
            "waveforms012.hdf5":
            "waveforms013.hdf5":
            "waveforms014.hdf5":
            "waveforms015.hdf5":
            "waveforms016.hdf5":
            "waveforms017.hdf5":
            "waveforms018.hdf5":
            "waveforms019.hdf5":
            "waveforms020.hdf5":
            "waveforms021.hdf5":
            "waveforms022.hdf5":
            "waveforms023.hdf5":
            "waveforms024.hdf5":
            "waveforms025.hdf5":
            "waveforms026.hdf5":
            "waveforms027.hdf5":
            "waveforms028.hdf5":
            "waveforms029.hdf5":
            "waveforms030.hdf5":
            "waveforms031.hdf5":
            "waveforms032.hdf5":
            "waveforms033.hdf5":
            "waveforms034.hdf5":
            "waveforms035.hdf5":
            "waveforms036.hdf5":
            "waveforms037.hdf5":
            "waveforms038.hdf5":
            "waveforms039.hdf5":
            "waveforms040.hdf5":
            "waveforms041.hdf5":
            "waveforms042.hdf5":
            "waveforms043.hdf5":
            "waveforms044.hdf5":
            "waveforms045.hdf5":
            "waveforms046.hdf5":
            "waveforms047.hdf5":
            "waveforms048.hdf5":
            "waveforms049.hdf5":
            "waveforms050.hdf5":
            "waveforms052.hdf5":
            "waveforms053.hdf5":
            "waveforms054.hdf5":
            "waveforms055.hdf5":
            "waveforms056.hdf5":
            "waveforms057.hdf5":
            "waveforms058.hdf5":
            "waveforms059.hdf5":
            "waveforms060.hdf5":
            "waveforms061.hdf5":
            "waveforms062.hdf5":
            "waveforms063.hdf5":
            "waveforms064.hdf5":
            "waveforms065.hdf5":
            "waveforms066.hdf5":
            "waveforms067.hdf5":
            "waveforms068.hdf5":
            "waveforms069.hdf5":
            "waveforms070.hdf5":
            "waveforms071.hdf5":
            "waveforms072.hdf5":
            "waveforms073.hdf5":
            "waveforms074.hdf5":
            "waveforms075.hdf5":
            "waveforms076.hdf5":
            "waveforms077.hdf5":
            "waveforms078.hdf5":
            "waveforms079.hdf5":
            "waveforms080.hdf5":
            "waveforms081.hdf5":
            "waveforms082.hdf5":
            "waveforms083.hdf5":
            "waveforms084.hdf5":
            "waveforms085.hdf5":
            "waveforms086.hdf5":
            "waveforms087.hdf5":
            "waveforms088.hdf5":
            "waveforms089.hdf5":
            "waveforms090.hdf5":
            "waveforms091.hdf5":
            "waveforms092.hdf5":
            "waveforms093.hdf5":
            "waveforms094.hdf5":
            "waveforms095.hdf5":
            "waveforms096.hdf5":
            "waveforms097.hdf5":
            "waveforms098.hdf5":
            "waveforms099.hdf5":
            "waveforms100.hdf5":
            "waveforms101.hdf5":
            "waveforms102.hdf5":
            "waveforms103.hdf5":
            "waveforms104.hdf5":
            "waveforms105.hdf5":
            "waveforms106.hdf5":
            "waveforms107.hdf5":
            "waveforms108.hdf5":
            "waveforms109.hdf5":
            "waveforms110.hdf5":
            "waveforms111.hdf5":
            "waveforms112.hdf5":
            "waveforms113.hdf5":
            "waveforms114.hdf5":
            "waveforms115.hdf5":
            "waveforms116.hdf5":
            "waveforms117.hdf5":
            "waveforms118.hdf5":
            "waveforms119.hdf5":
            "waveforms120.hdf5":
            "waveforms121.hdf5":
            "waveforms122.hdf5":
            "waveforms123.hdf5":
            "waveforms124.hdf5":
            "waveforms125.hdf5":
            "waveforms126.hdf5":
            "waveforms127.hdf5":
            "waveforms128.hdf5":
            "waveforms129.hdf5":
            "waveforms130.hdf5":
            "waveforms131.hdf5":
            "waveforms132.hdf5":
            "waveforms133.hdf5":
            "waveforms134.hdf5":
            "waveforms135.hdf5":
            "waveforms136.hdf5":
            "waveforms137.hdf5":
            "waveforms138.hdf5":
            "waveforms139.hdf5":
            "waveforms140.hdf5":
            "waveforms141.hdf5":
            "waveforms142.hdf5":
            "waveforms143.hdf5":
            "waveforms144.hdf5":
            "waveforms145.hdf5":
            "waveforms146.hdf5":
            "waveforms147.hdf5":
            "waveforms148.hdf5":
            "waveforms149.hdf5":
            "waveforms150.hdf5":
            "waveforms151.hdf5":
            "waveforms152.hdf5":
            "waveforms153.hdf5":
            "waveforms154.hdf5":
            "waveforms155.hdf5":
            "waveforms156.hdf5":
        }

        metadata_name = f"metadata{chunk}.csv"
        waveform_name = f"waveforms{chunk}.hdf5"
        seisbench.util.download_http(
            files[metadata_name] + "/download",
            path / writer.metadata_path,
            desc=f"Downloading {metadata_name}",
        )
        seisbench.util.download_http(
            files[waveform_name] + "/download",
            path / writer.waveforms_path,
            desc=f"Downloading {waveform_name}",
        )
