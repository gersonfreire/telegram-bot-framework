
## Você

Is there any way to automate the part of pull the last changes on server?

## Copilot

Absolutely! You can automate this process using a tool like Git hooks or a CI/CD pipeline. Here’s a simple way to automate the pull using a Git hook:

### Using Git Hooks

1. **SSH into Your Server** :

```
   ssh yourUsername@yourServerIP
```

1. **Navigate to Your Project Directory** :

```
   cd/path/to/your/project
```

1. **Create or Edit the Post-Receive Hook** : Navigate to the `hooks` directory inside your Git project:

```
   cd.git/hooks
```

   Create or edit the `post-receive` hook:

```
   nano post-receive
```

1. **Add the Following Script** :

```
   #!/bin/sh
   GIT_WORK_TREE=/path/to/your/project git checkout -f
   # Command to restart your application, e.g., PM2
   pm2 restart yourAppName
```

1. **Make the Hook Executable** :

```
   chmod+x post-receive
```

Now, every time you push to your GitHub repository, the server will automatically pull the latest changes and restart the application.

### Using CI/CD Pipelines

Alternatively, you can set up a CI/CD pipeline using a service like GitHub Actions, Jenkins, or GitLab CI/CD. This allows for more complex workflows and better integration with your development process.

 **Example with GitHub Actions** :

1. **Create a ** `.github/workflows/deploy.yml` ** file in your GitHub repository** :

```
   name:Deploy

   on:
     push:
       branches:
         -main

   jobs:
     deploy:
       runs-on:ubuntu-latest

       steps:
       -name:Checkoutcode
         uses:actions/checkout@v2

       -name:Deploytoserver
         uses:appleboy/ssh-action@v0.1.3
         with:
           host:${{secrets.HOST}}
           username:${{secrets.USERNAME}}
           key:${{secrets.SSH_KEY}}
           script:|
             cd /path/to/your/project
             git pull origin main
             pm2 restart yourAppName
```

1. **Add your server's SSH details to GitHub Secrets** : Go to your repository settings, then "Secrets," and add `HOST`, `USERNAME`, and `SSH_KEY`.

This way, GitHub Actions will handle the deployment process every time you push changes to the main branch.

Take your pick! Both methods will save you a lot of manual work. 🚀
