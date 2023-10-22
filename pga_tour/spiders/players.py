import scrapy
import pandas as pd


class PlayersSpider(scrapy.Spider):
    name = "players"
    allowed_domains = ["pgatourmediaguide.com"]
    start_urls = ["https://www.pgatourmediaguide.com/player"]

    def parse(self, response):
        # get all players link
        players = response.css("main a.player-item")
        for p in players:
            url = response.urljoin(p.attrib.get("href"))
            player_name = p.css("h6::text").get().strip()
            yield scrapy.Request(
                url,
                meta=dict(player_name=player_name),
                callback=self.parse_table,
            )

    def parse_table(self, response):
        # get met
        i = response.meta

        # get the table
        first_row = response.css("table thead tr:first-child").get()
        footer = response.css("table tfoot").get()
        table = response.css("table").get()
        table = table.replace(first_row, "")
        table = table.replace(footer, "")
        dfs = pd.read_html(table)
        df = dfs[0]
        df = df.fillna("")
        # get the columns
        columns = [col[0] for col in df.columns]
        # get the values
        item = {
            "Player": i.get("player_name", ""),
        }
        for row in df.values:
            for key, value in zip(columns, row):
                item.update({key: value})
            yield item
