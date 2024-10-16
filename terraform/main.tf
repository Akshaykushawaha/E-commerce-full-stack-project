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
  ami           = "ami-02db68a01488594c5"  # Update this to the correct AMI ID for us-east-1
  instance_type = "t2.micro"
  vpc_security_group_ids = [aws_security_group.instance.id]

  user_data     = <<-EOF
              #!/bin/bash
              sudo apt-get update -y

              # Install Docker
              sudo apt-get install -y docker.io
              sudo systemctl start docker
              sudo systemctl enable docker

              # Install Jenkins
              sudo apt-get install -y openjdk-11-jdk  # Install Java (required for Jenkins)
              wget -q -O - https://pkg.jenkins.io/debian/jenkins.io.key | sudo apt-key add -
              sudo sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
              sudo apt-get update -y
              sudo apt-get install -y jenkins
              sudo systemctl start jenkins
              sudo systemctl enable jenkins

              # Install Python, Flask, and pip dependencies
              sudo apt-get install -y python3-pip
              pip3 install flask

              # Install Selenium, Chrome, and Chrome WebDriver
              sudo apt-get install -y wget unzip
              wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
              sudo dpkg -i google-chrome-stable_current_amd64.deb || sudo apt-get install -f -y
              wget https://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip
              unzip chromedriver_linux64.zip
              sudo mv chromedriver /usr/bin/chromedriver
              sudo chmod +x /usr/bin/chromedriver

              # Install Selenium
              pip3 install selenium
              EOF

  tags = {
    Name = "flask-app"
  }
}
