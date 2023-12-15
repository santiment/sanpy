podTemplate(label: 'sanpy-builder', containers: [
    containerTemplate(name: 'python', image: 'python:3.8-buster', command: 'cat', ttyEnabled: true)
]) {
  node('sanpy-builder') {
    stage('Run Tests') {
      container('python') {
        def scmVars = checkout scm
        sh "python3 setup.py test" 
      }
    }

    stage('Update deployment') {
      container('python') {

        if (env.BRANCH_NAME == "master") {
          withCredentials([
              usernamePassword(
                credentialsId: 'test_pypi_org',
                passwordVariable: 'test_pypi_org_psw',
                usernameVariable: 'test_pypi_org_usr'
              )
            ]){
        
            sh "python3 -m pip install --user --upgrade setuptools>=38.6.0 wheel>=0.31.0 twine>=1.11.0"
            sh "python3 setup.py sdist bdist_wheel"
            sh "~/.local/bin/twine upload -u __token__ -p ${test_pypi_org_sanpy_publishing_api_token} --repository-url https://test.pypi.org/legacy/ dist/*"
            }
        }
      }
    }
  }
}


