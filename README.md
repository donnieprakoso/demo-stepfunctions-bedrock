# Build and Enrich Your Generative AI Apps with Visual Workflow 

Hey there 👋

This repository holds all source code for demos that I use for my session at AWS Innovate AI/ML. 
I also wrote an article describing my [5 lessons learned in building generative AI application with a workflow](https://community.aws/content/2fiK2xJf773295nAEE9ecLgtvFP/5-lessons-learned-in-building-generative-ai-application-with-a-workflow). So, if you haven't read that article, I suggest you to read my post first to give you a bit of context. 

## Tl;dr: How to use this repo?

All of the demo is ready for you to deploy using AWS Cloud Development Kit (CDK). Once you have bootstrapped your account, the demos are fairly easy for you to deploy. Just run:

```
$> cdk deploy
```

...and it will ready for you to use.

And, if you no longer need it, you can simply run 

```
$> cdk destroy
```

...and it will be removed from your account. 


## Modules

There are 4 modules in total. Below table shows the description and the direct link for easy access.

| Module Number  | Description |
| -------------  | ----------- |
| 1 Model Invoke |  This demo shows a basic (and mostly used) AWS StepFunctions integration with Amazon Bedrock |
| 2 Prompt Chaining | This demo shows how you can implement prompt chaining | 
| 3 Parallel Chaining | Shows multiple workflows that can run at the same time |
| 4 HTTPS Endpoint | Shows how to integrate with Amazon EventBridge API Destinations to call external APIs |

Happy building!
