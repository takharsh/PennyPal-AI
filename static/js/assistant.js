// Assistant Chatbot Script
let chatHistory = [];

document.addEventListener('DOMContentLoaded', () => {
  const sendBtn = document.getElementById('chat-send-btn');
  const chatInput = document.getElementById('chat-user-input');
  const clearBtn = document.getElementById('clear-chat-btn');

  if (sendBtn && chatInput) {
    sendBtn.addEventListener('click', () => sendChatMessage());
    chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendChatMessage();
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      const historyContainer = document.getElementById('chat-history');
      if (historyContainer) {
        historyContainer.innerHTML = `
          <div class="chat-bubble ai">
            Chat history cleared. Hello! How can I assist with your financial decisions today?
          </div>
        `;
        chatHistory = [];
      }
    });
  }
});

function sendSuggestedPrompt(element) {
  const promptText = element.innerText;
  const chatInput = document.getElementById('chat-user-input');
  if (chatInput) {
    chatInput.value = promptText;
    sendChatMessage();
  }
}

async function sendChatMessage() {
  const input = document.getElementById('chat-user-input');
  const historyContainer = document.getElementById('chat-history');
  if (!input || !historyContainer) return;

  const userPrompt = input.value.trim();
  if (!userPrompt) return;

  // Render User Message Bubble
  const userBubble = document.createElement('div');
  userBubble.className = 'chat-bubble user';
  userBubble.innerText = userPrompt;
  historyContainer.appendChild(userBubble);

  input.value = '';
  historyContainer.scrollTop = historyContainer.scrollHeight;

  // Render Loading Bubble
  const loadingBubble = document.createElement('div');
  loadingBubble.className = 'chat-bubble ai';
  loadingBubble.id = 'ai-loading-bubble';
  loadingBubble.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-1"></i> PennyPal AI is analyzing your database context...';
  historyContainer.appendChild(loadingBubble);
  historyContainer.scrollTop = historyContainer.scrollHeight;

  // Disable send button while processing
  const sendBtn = document.getElementById('chat-send-btn');
  if (sendBtn) sendBtn.disabled = true;

  try {
    const response = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt: userPrompt,
        history: chatHistory.map(h => `${h.role}: ${h.text}`).join('\n')
      })
    });
    const data = await response.json();

    loadingBubble.remove();

    if (data.success) {
      const aiBubble = document.createElement('div');
      aiBubble.className = 'chat-bubble ai';
      aiBubble.innerHTML = data.response.replace(/\n/g, '<br>');
      historyContainer.appendChild(aiBubble);

      // Save to local history array
      chatHistory.push({ role: 'User', text: userPrompt });
      chatHistory.push({ role: 'Assistant', text: data.response });
    } else {
      const errorBubble = document.createElement('div');
      errorBubble.className = 'chat-bubble ai';
      errorBubble.innerText = data.message || 'Sorry, I encountered an error processing your query.';
      historyContainer.appendChild(errorBubble);
    }
  } catch (err) {
    if (loadingBubble) loadingBubble.remove();
    const errorBubble = document.createElement('div');
    errorBubble.className = 'chat-bubble ai';
    errorBubble.innerText = 'Unable to communicate with AI Assistant service. Please try again.';
    historyContainer.appendChild(errorBubble);
  } finally {
    if (sendBtn) sendBtn.disabled = false;
    historyContainer.scrollTop = historyContainer.scrollHeight;
  }
}
