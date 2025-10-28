---
layout: welcome
title: Hi, I'm Huy Dũng (DaveHD)
cover: false
sitemap: false
# projects_page: projects.md
---

Since 2008, I've been passionate about three things:
- **Building tech products** that enhance the human experience - software, websites, games
- **Delivering training, coaching, and mentorship** that helps people grow
- **Creating work environments** where teams can achieve great results and thrive as individuals

My life and work are guided by five values: **Take Ownership**, **Seek Clarity**, **Be Effective**, **Stay Balanced**, and **Embrace Humanity**.

On this site, I share my thoughts on {% assign filtered_categories = site.featured_categories | where_exp: "item", "item.menu != true" %}{% for category in filtered_categories %}[{{ category.title }}]({{ category.url }}){% if forloop.last == false and forloop.rindex > 2 %}, {% elsif forloop.rindex == 2 %} and {% endif %}{% endfor %}.

## I've got the honored to speak at

{% include speaking-section.html %}

---

## Let's Connect: [Ask me anything](https://docs.google.com/forms/d/e/1FAIpQLSeYmMIn9eZgPpUE6J0SPeUaMPN5KABRE_al-GRZkD2mDeW-Vw/viewform), or [book a free call](https://calendly.com/huydung/clarity-call)!
