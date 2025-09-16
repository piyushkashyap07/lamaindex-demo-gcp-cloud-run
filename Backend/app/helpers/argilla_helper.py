import os
import argilla as rg
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("ARGILLA_API_URL:", os.getenv("ARGILLA_API_URL"))
print("ARGILLA_API_KEY:", os.getenv("ARGILLA_API_KEY"))

def argilla_dataset():
    # Create an Argilla client
    client = rg.Argilla(
        api_url=os.environ["ARGILLA_API_URL"],
        api_key=os.environ["ARGILLA_API_KEY"],
    )
    
    try:
        # Check if workspace exists or create it
        workspace = client.workspaces("new-workspace")
        if not workspace:
            from argilla.workspaces import Workspace
            workspace = Workspace(name="new-workspace", client=client)
            client.workspaces.add(workspace)
        
        # Create dataset with fields and questions
        from argilla.datasets import Dataset
        from argilla.settings import Settings
        # Correct import paths based on documentation
        from argilla.settings import TextField, RatingQuestion, TextQuestion
        
        settings = Settings(
            fields=[
                TextField(name="query"),
                TextField(name="prompt"),
                TextField(name="agent_name"),
                TextField(name="summary")
            ],
            questions=[
                RatingQuestion(
                    name="response-rating",
                    description="How would you rate the quality of the response?",
                    values=[1, 2, 3, 4, 5],
                    required=True,
                ),
                TextQuestion(
                    name="response-feedback",
                    description="What feedback do you have for the response?",
                    required=False,
                ),
            ],
            guidelines="You're asked to rate the quality of the response and provide feedback.",
        )
        
        # Try to get existing dataset or create a new one
        dataset = client.datasets("propensity-score-feedback", workspace=workspace)
        if not dataset:
            dataset = Dataset(
                name="propensity-score-feedback", 
                workspace=workspace,
                settings=settings,
                client=client
            )
            client.datasets.add(dataset)
            
        return dataset
        
    except Exception as e:
        print(f"Error: {e}")

    