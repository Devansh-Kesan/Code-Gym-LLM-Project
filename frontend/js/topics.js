document.addEventListener("DOMContentLoaded", async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const courseId = urlParams.get("course_id");
    const container = document.getElementById("topics");
  
    if (!courseId) {
      container.innerHTML = "<p>Course ID missing in URL.</p>";
      return;
    }
  
    try {
      const res = await fetch(`http://localhost:8000/courses/${courseId}/topics`);
      const topics = await res.json();
      console.log(topics)
      topics.forEach(topic => {
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `
          <h3>${topic.topic_title}</h3>
          <p>${topic.short_description}</p>
        `;
        card.onclick = () => {
          window.location.href = `questions.html?course_id=${courseId}&topic_id=${topic.topic_id}`;
        };
        container.appendChild(card);
      });
    } catch (error) {
      console.error("Error loading topics:", error);
      container.innerHTML = "<p>Failed to load topics. Try again later.</p>";
    }
  });
  