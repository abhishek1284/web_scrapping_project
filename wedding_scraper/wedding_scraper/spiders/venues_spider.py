import scrapy
import re


class VenuesSpider(scrapy.Spider):
    name = "wedding_venues"
    allowed_domains = ["wedding-spot.com"]
    start_urls = [f"https://www.wedding-spot.com/wedding-venues/?page={i}" for i in range(1, 38)]

    def parse(self, response):
        venue_links = response.css('a[href*="/venue/"]::attr(href)').getall()
        for link in set(venue_links):
            if "/venue/" in link:
                full_url = response.urljoin(link.split('?')[0])
                yield scrapy.Request(full_url, callback=self.parse_venue)

    def parse_venue(self, response):
        def extract_phone():
            phone = response.css('a.venue-phone::text, .phone-number::text').get()
            if phone:
                return phone.strip()
            span_texts = response.css("span::text").getall()
            for text in span_texts:
                match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
                if match:
                    return match.group()
            return "N/A"

        def extract_section(header_text):
            header = response.xpath(f'//h3[contains(text(),"{header_text}")]')
            if header:
                sibling = header.xpath('./following-sibling::*[1]')
                if sibling:
                    return sibling.xpath('string(.)').get().strip()
            return "N/A"

        def extract_highlights():
            highlights = response.css('div.VenueHighlights--label::text').getall()
            if highlights:
                return "; ".join([h.strip() for h in highlights])
            return "N/A"

        

        yield {
            "URL": response.url,
            "Venue Name": response.css('h1.venue-title::text, h1::text').get(default='N/A').strip(),
            "Phone": extract_phone(),
            "Venue Highlights": extract_highlights(),
            "Guest Capacity": extract_section("Guest capacity:"),
            "Location": extract_section("Location:"),
        }
