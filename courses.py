import scrapy
import json
from pathlib import Path

class CoursesSpider(scrapy.Spider):
    name = "courses"
    allowed_domains = ["talentedge.com"]
    start_urls = ["https://talentedge.com/browse-courses"]

    def parse(self, response):
        # Save the content as files
        page = response.url.split("/")[-1]
        filename = f"courses-{page}.html"
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")

        courses_list = []

        # Ensure the CSS selector is correct for extracting course cards
        cards = response.css(".course-card")  # Adjust this based on actual HTML structure
        if not cards:
            self.log("No course cards found. Check the CSS selector.")

        for card in cards:
            # Extract course details
            course_url = card.css("a::attr(href)").get()
            course_title = card.css("a::text").get()
            course_description = card.css(".course-description::text").get(default='N/A')
            course_duration = card.css(".course-duration::text").get(default='N/A')
            course_time = card.css(".course-time::text").get(default='N/A')
            course_start_date = card.css(".course-start-date::text").get(default='N/A')
            course_will_learn = card.css(".what-will-learn::text").get(default='N/A')
            course_skills = card.css(".skills::text").get(default='N/A')
            course_target_students = card.css(".target-students::text").get(default='N/A')
            
            # Follow the link to the course page
            yield response.follow(course_url, self.parse_course, meta={
                'title': course_title,
                'description': course_description,
                'duration': course_duration,
                'time': course_time,
                'start_date': course_start_date,
                'will_learn': course_will_learn,
                'skills': course_skills,
                'target_students': course_target_students
            })

    def parse_course(self, response):
        # Extract additional course details
        course_fee = response.css(".course-fee::text").get(default='N/A')
        course_instructors = response.css(".course-instructors::text").getall()
        course_rating = response.css(".course-rating::text").get(default='N/A')
        course_reviews = response.css(".course-reviews::text").get(default='N/A')

        # Combine data
        course_data = {
            'url': response.url,
            'title': response.meta['title'],
            'description': response.meta['description'],
            'duration': response.meta['duration'],
            'time': response.meta['time'],
            'start_date': response.meta['start_date'],
            'will_learn': response.meta['will_learn'],
            'skills': response.meta['skills'],
            'target_students': response.meta['target_students'],
            'fee': course_fee,
            'instructors': course_instructors,
            'rating': course_rating,
            'reviews': course_reviews
        }

        # Save the updated courses data as a JSON file
        json_filename = f'courses-{response.url.split("/")[-1]}.json'
        with open(json_filename, 'w') as f:
            json.dump(course_data, f, indent=4)
        self.log(f"Saved JSON file {json_filename}")
