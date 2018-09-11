podTemplate(label: 'sanpy-builder', containers: [
  containerTemplate(name: 'docker', image: 'docker', ttyEnabled: true, command: 'cat', envVars: [
    envVar(key: 'DOCKER_HOST', value: 'tcp://docker-host-docker-host:2375')
  ])
]) {
  node('sanpy-builder') {
    stage('Build') {
      echo 'Dummy Jenkinsfile just to trigger the "Deploy sanpy to test.pypi.org"'
    }
  }
}
