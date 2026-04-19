import subprocess
import os

def run():
    print("Starting scheduled AI blog update...")
    # Navigate to the correct directory
    os.chdir("/home/harshit/.openclaw/workspace/ai-money-machine")
    
    # We want to run the core logic to research and write a post.
    # Since AGENT.md describes a process usually done by the agent,
    # we'll use a specialized script or simply rely on the main agent turn.
    
    # For now, let's just trigger a dummy commit to verify cron is working,
    # and then I'll set up the real logic.
    print("Researching and writing post...")
    # (Logic to call Firecrawl and write files would go here)
    
if __name__ == "__main__":
    run()
