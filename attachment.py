import base64
from apiclient import errors

def save(service, msgId, attId, storeDir, filename, userId='me'):
    try:
        att = service.users().messages().attachments().get(
            userId = userId, 
            messageId = msgId, 
            id = attId).execute()
        file_data = base64.urlsafe_b64decode(
            att['data'].encode('UTF-8'))
        path = ''.join([storeDir, filename])
        # print('Save to: %s' % path)
        f = open(path, 'wb')
        f.write(file_data)
        f.close()

    except Exception as e:
        print('An error occurred %s' % e)

def GetAttachments(service, user_id, msg_id, store_dir):
    """Get and store attachment from Message with given id.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: ID of Message containing attachment.
    store_dir: The directory used to store attachments.
  """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()

        for part in message['payload']['parts']:
            if part['filename']:
                file_data = base64.urlsafe_b64decode(part['body']['data']
                                                     .encode('UTF-8'))

                path = ''.join([store_dir, part['filename']])

                f = open(path, 'w')
                f.write(file_data)
                f.close()
            for p in (p for p in part['parts'] if 'attachmentId' in p['body'].keys()):
                print('filename: %s' % p['filename'])
                print('attachmentId: %s' % p['body']['attachmentId'])
                att_id = p['body']['attachmentId']
                att = service.users().messages().attachments().get(
                    userId=user_id, messageId=msg_id, id=att_id).execute()
                file_data = base64.urlsafe_b64decode(
                    att['data'].encode('UTF-8'))
                # print('file_data: %s' % file_data)
                path = ''.join([store_dir, p['filename']])
                print('path: %s' % path)
                f = open(path, 'wb')
                f.write(file_data)
                f.close()
    except Exception as e:
        print('An error occurred %s' % e)
