provider "aws" {
  region = "us-east-1"
}

resource "aws_security_group" "instance" {
  name        = "allow_ssh_http"
  description = "Allow inbound traffic on SSH and HTTP"
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 443  # Optional: Allow HTTPS traffic
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "app" {
  ami           = "ami-06b21ccaeff8cd686"  # Update this to the correct AMI ID for us-east-1
  instance_type = "t2.micro"
  vpc_security_group_ids = [aws_security_group.instance.id]

    user_data     = <<-EOF
            #!/bin/bash
            set -e  # Exit on any error

            # Update the package repository
            sudo yum update -y

            sudo yum install git -y


            # Install Docker
            sudo yum install -y docker
            sudo systemctl start docker
            sudo systemctl enable docker

            sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            # Set the permissions to make it executable
            sudo chmod +x /usr/local/bin/docker-compose
            docker-compose --version

            # Install Jenkins
            sudo wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
            sudo rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io-2023.key
            sudo yum upgrade
            sudo dnf install java-17-amazon-corretto -y
            sudo yum install jenkins -y
            sudo systemctl enable jenkins
            sudo systemctl start jenkins
            sudo systemctl status jenkins

            # Install Python and pip
            sudo yum install -y python3
            sudo yum install -y python3-pip  # Explicitly install pip

            # Install Flask
            sudo pip3 install flask

            # Install Selenium, Chrome, and Chrome WebDriver
            sudo yum install -y wget unzip

            # Install Google Chrome
            sudo curl https://intoli.com/install-google-chrome.sh | bash
            sudo mv /usr/bin/google-chrome-stable /usr/bin/google-chrome
            google-chrome --version && which google-chrome

            # Install ChromeDriver
            sudo wget https://chromedriver.storage.googleapis.com/80.0.3987.106/chromedriver_linux64.zip
            sudo unzip chromedriver_linux64.zip
            sudo mv chromedriver /usr/bin/chromedriver
            chromedriver --version
            sudo chmod +x /usr/bin/chromedriver

            # Install Selenium
            sudo pip3 install selenium
    EOF


  tags = {
    Name = "flask-app"
  }
}
