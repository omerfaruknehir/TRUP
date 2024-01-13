import glob
import hashlib
import os
import datetime
from infrastructure.locker import LockDirectory

class SessionManager:
    data_path = "data/sessions"
    _sessions = [None]
    _loaded = False

    def _check_load():
        if not SessionManager._loaded:
            raise BrokenPipeError("SessionManager did not load.")
        if SessionManager._sessions == [None]:
            raise BrokenPipeError("SessionManager did not load correctly!")

    def generate_session_id():
        SessionManager._check_load()
        res = hashlib.sha256(os.urandom(8)).hexdigest()
        while res in SessionManager._sessions:
            res = hashlib.sha256(os.urandom(8)).hexdigest()
        SessionManager._sessions.append(res)
        return res
    
    def load():
        SessionManager._sessions = []
        existing_corrupts = len(glob.glob(f"{SessionManager.data_path}/corrupts/*.session"))
        corrupted_number = 0
        removed_number = 0
        files = glob.glob(f"{SessionManager.data_path}/*.session")
        for path in files:
            with open(path, "r", encoding="utf-8") as sessionfile:
                sessiondata = sessionfile.read().split(";")
            if len(sessiondata) != 4:
                corrupted_number += 1
                os.rename(path, f"{SessionManager.data_path}/corrupts/{os.path.basename(path)}")
            else:
                try:
                    age = (datetime.datetime.utcnow() - datetime.datetime.strptime(sessiondata[2], '%Y-%m-%d %H:%M:%S %Z'))
                    lifespan = datetime.timedelta(days=sessiondata[3].split(',')[0], seconds=sessiondata[3].split(',')[1])
                except ValueError:
                    corrupted_number += 1
                    os.rename(path, f"{SessionManager.data_path}/corrupts/{os.path.basename(path)}")
                    continue
                if age > lifespan:
                    removed_number += 1
                    os.remove(path)
                else:
                    SessionManager._sessions.append(os.path.basename(path).removesuffix(".session"))
        print(f"{len(files)} session files processed, {removed_number} session files expired lifespan, {corrupted_number} corrupted session file found and {len(SessionManager._sessions)} session files loaded correctly. Total corrupted session file number is {corrupted_number + existing_corrupts}")
        SessionManager._loaded = True

    def add_session(user_id, on_success, lifespan:datetime.timedelta=datetime.timedelta(0, seconds=60)):
        """
            
        """
        
        SessionManager._check_load()
        session_id = SessionManager.generate_session_id()
        def days_seconds(td: datetime.timedelta):
            return str(td.days), str(td.seconds)
        try:
            with open(f"{SessionManager.data_path}/{session_id}.session", "w", encoding="utf-8") as sessionfile:
                #def days_hours_minutes(td):
                #    return td.days, td.seconds//3600, (td.seconds//60)%60
                data = f"{user_id};{on_success};{datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S %Z')};{','.join(days_seconds(lifespan))}"
                sessionfile.write(data)
            SessionManager._sessions.append(str(session_id))
        except Exception as e:
            os.rename(f"{SessionManager.data_path}/{session_id}.session", f"{SessionManager.data_path}/corrupts/{session_id}.session")
            raise e
        return session_id

    def remove_session(session_id):
        SessionManager._check_load()
        if session_id not in SessionManager._sessions:
            return False
        SessionManager._sessions.remove(session_id)
        os.remove(f"{SessionManager.data_path}/{session_id}.session")
        return True

    def get_session(session_id: int):
        """
            output: `list` => [
            
                `user_id`,

                `on_success`,

                `date_created (in this format: "%Y-%m-%d %H:%M:%S %Z", Z is UTC})`,

                `lifespan (in this format: "days, seconds")`

            ]
        """
        SessionManager._check_load()
        if session_id not in SessionManager._sessions:
            raise None
        with open(f"{SessionManager.data_path}/{session_id}.session", "r", encoding="utf-8") as sessionfile:
            sessiondata = sessionfile.read()
        print(sessiondata)
        return sessiondata.split(';')